import time
import random
from typing import Any, Dict, List, Tuple, Union
from geopy.distance import geodesic
from asyncio import sleep

from networkx.classes.graph import Graph

from util import *
from samplegen import sample
from const import POINT_BATCH, SAMPLE_PERIOD
import pathgen

class Runner :
    sess : YZSession
    device_name : str
    sdk_version : str
    app_version : str


    def __init__(self, sess: YZSession) -> None:
        self.sess = sess


    async def get_tasks(self) -> List[dict]:
        resp_json = await self.sess.APIpost_json('/run/getHomeRunInfo')
        return resp_json['cralist']
    

    async def __start_run(self, task : Dict) -> Tuple[int, str]:
        data = {
            'raId': str(task['id']),
            'raRunArea': task['raRunArea'],
            'raType': task['raType']
        }

        if task.get('isMorning', '') == 'R1':
            data['isMorning'] = 'R1'
        
        resp = await self.sess.APIpost_json('/run/start', data=data)

        if resp.get('canSport') == 'N':
            raise YZError('sport is blocked. Reason: '+ resp.get('warnContent'))
        if resp.get('warnContent') != '':
            print('YZ sport warning: ' + resp['warnContent'])

        return resp['id'], resp['recordStartTime']


    async def __finish_run(
        self,
        task : dict,
        id : int,
        start_time : str,
        check_points : Union[List[dict], None],
        uncheck_points : Union[List[dict], None],
        distance : float,
        cadence : float,
        duration : int
    ) -> None:

        distance_km = distance / 1000
        duration_min = duration / 60
        data = {}

        if check_points:
            send_points = []
            for i in check_points:
                send_points.append({
                    'point': f'{i[1]},{i[0]}',
                    'marked': 'Y',
                    'index': str(len(send_points))
                })
            for i in uncheck_points:
                send_points.append({
                    'point': f'{i[1]},{i[0]}',
                    'marked': 'N',
                    'index': ''
                })
            data['manageList'] = send_points

        data.update({
            'recordMileage': '{:.2f}'.format(distance_km),
            'recodeCadence': str(int(cadence)),
            'recodePace': '{:.2f}'.format(duration_min / distance_km),
            'deviceName': self.device_name,
            'sysEdition': self.sdk_version,
            'appEdition': self.app_version,
            'raIsStartPoint' : 'Y' if check_points else 'N',
            'raIsEndPoint' : 'Y' if check_points else 'N',
            'raRunArea': task['raRunArea'],
            'recodeDislikes': str(len(check_points)) if check_points else '0',
            'raId': str(task['id']),
            'raType': task['raType'],
            'id': str(id),
            'duration': str(duration),
            'recordStartTime': start_time
        })

        await self.sess.APIpost_json('/run/finish', data=data)


    async def __send_points(
        self,
        id : int,
        points : dict
    ) -> None:
        await self.sess.APIpost_json('/run/splitPoints', data={
            'cardPointList': [{
                'point': f'{i[0][1]},{i[0][0]}',
                'runStatus': '1',
                'speed': '{:.2f}'.format(mpers2minperkm(i[1]))
                } for i in points],
            'crsRunRecordId': str(id),
            'schoolId': self.sess.school_id,
            'userName': self.sess.account_id
        }, auth_headers=False)


    async def run(self, task : Dict, graph : Graph, min_distance : float, cadence : float, speed1 : float, speed2 : float) -> None:
        pass_path : dict
        points = parse_points(task['points'])
        card_range = task['cardRange']

        if task['raType'] == 'T1':
            pass_path = pathgen.T1Generate(graph, points, min_distance, card_range)
        elif task['raType'] == 'T2':
            pass_path = pathgen.T2Generate(graph, min_distance)
        elif task['raType'] == 'T3':
            pass_path = pathgen.T3Generate(graph, points, task['raDislikes'], min_distance, card_range)
        else:
            raise YZError(f"Unknown task type {task['raType']}")
        
        sample_path = sample(pass_path, speed1, speed2)
        sample_path_len = len(sample_path)
        id, start_time = await self.__start_run(task)
        
        sent_ind = 0
        cur_ind = 0

        start_timestamp = time.time()

        last_point = None
        managed_point = []
        distance = 0.0

        for point_speed in sample_path:
            managed_point.extend(filter((lambda n: geodesic(n, point_speed[0]).m <= card_range), points))
            points = list(filter((lambda n: geodesic(n, point_speed[0]).m > card_range), points))
            if last_point:
                distance += geodesic(last_point, point_speed[0]).m
            last_point = point_speed[0]

        managed_point = managed_point[:task['raDislikes']]

        while sent_ind != sample_path_len:
            ttime = time.time()
            cur_ind = min(sample_path_len, int((ttime - start_timestamp) // (SAMPLE_PERIOD / 1000)))
            if cur_ind - sent_ind >= POINT_BATCH or cur_ind == sample_path_len:
                try:
                    await self.__send_points(id, sample_path[sent_ind:cur_ind])
                    sent_ind = cur_ind
                    print(f'Progress: {sent_ind}/{sample_path_len}')
                except BaseException as err:
                    print(f'Got error when send points: {err}\nTry again...')
                    await sleep(5)
                    # raise err
            else:
                await sleep((POINT_BATCH + sent_ind) * SAMPLE_PERIOD / 1000 - (ttime - start_timestamp))
        
        while True:
            try:
                await self.__finish_run(
                    task,
                    id,
                    start_time,
                    managed_point,
                    points[:task['raDislikes']-len(managed_point)],
                    distance,
                    cadence,
                    (SAMPLE_PERIOD * sample_path_len) // 1000 + random.randint(
                        0,
                        (SAMPLE_PERIOD * sample_path_len) // 10000
                    )
                )
            except BaseException as err:
                print(f'Got error when send finishing: {err}\nTry again...')
                await sleep(5)
            else:
                break