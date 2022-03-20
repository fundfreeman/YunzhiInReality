from networkx.classes.graph import Graph
from geopy.distance import geodesic
import asyncio
import aiohttp

from const import APP_EDITION
from util import YZSchool, minperkm2mpers, check_update
from running import Runner


g = Graph()

g.add_node(1, pos=(30.907553,118.71592 ))
g.add_node(2, pos=(30.907199,118.715786))
g.add_node(3, pos=(30.907088,118.716269))
g.add_node(4, pos=(30.90707 ,118.717004))
g.add_node(5, pos=(30.906913,118.717524))
g.add_node(6, pos=(30.907143,118.717358))
g.add_node(7, pos=(30.905657,118.717546))
g.add_node(8, pos=(30.905273,118.717727))
g.add_node(9, pos=(30.904478,118.716618))
g.add_node(10, pos=(30.905141,118.71599 ))
g.add_node(11, pos=(30.903585,118.715261))
g.add_node(12, pos=(30.904253,118.714665))
g.add_node(13, pos=(30.904911,118.71408 ))
g.add_node(14, pos=(30.905629,118.715019))
g.add_node(15, pos=(30.906416,118.715438))
g.add_node(16, pos=(30.906203,118.715925))
g.add_node(17, pos=(30.905675,118.716274))
g.add_node(18, pos=(30.90568 ,118.716988))
g.add_node(19, pos=(30.906651,118.717004))
g.add_node(20, pos=(30.906628,118.716274))

def link(a, b):
    g.add_edge(a, b, dis=geodesic(g.nodes[a]['pos'], g.nodes[b]['pos']).m)

link(1, 6)
link(1, 2)
link(2, 3)
link(2, 15)
link(3, 4)
link(4, 5)
link(4, 19)
link(5, 6)
link(5, 7)
link(7, 8)
link(8, 9)
link(9, 10)
link(9, 11)
link(10, 12)
link(11, 12)
link(12, 13)
link(13, 14)
link(14, 15)
link(15, 16)
link(16, 20)
link(16, 17)
link(17, 18)
link(17, 20)
link(18, 19)
link(19, 20)


async def main():
    if not await check_update('http://81.70.49.179:8080/', '12'):
        print('Yunzhi application has been updated. This version of script is depriciated now')
        input()
        return
    
    try:
        school = YZSchool('http://210.45.246.53:8080/', '100')
        username = input('Username: ')
        password = input('Password: ')
        sess = await school.login(username, password)
        run = Runner(sess)

        run.app_version = APP_EDITION

        tasks = await run.get_tasks()
        
        print(tasks[0]['raName'])
        print(f"Task type: {tasks[0]['raType']}")
        print(f"Minimal journey: {tasks[0]['raSingleMileageMin']} km")
        print(f"Maximal journey: {tasks[0]['raSingleMileageMax']} km")
        print(f"Minimal step freq: {tasks[0]['raCadenceMin']} step/min")
        print(f"Maximal step freq: {tasks[0]['raCadenceMax']} step/min")
        print(f"Minimal speed: {tasks[0]['raPaceMin']} min/km")
        print(f"Maximal speed: {tasks[0]['raPaceMax']} min/km")

        print('Device name format: "Manufacturer(Model)"')
        print('Example: HUAWEI(OXF-AN10)')
        run.device_name = input('Device name: ')
        print('Android SDK version is a single integer')
        print('Example: 11')
        run.sdk_version = input('Android SDK version: ')
        dis = float(input('Jounary (m): '))
        cadence = float(input('Step freq (step/min): '))
        speed1 = float(input('Startup speed (min/km): '))
        speed2 = float(input('Continuous speed (min/km): '))

        print('Start simulating... DO NOT EXIT')
        await run.run(tasks[0], g, dis, cadence, minperkm2mpers(speed1), minperkm2mpers(speed2))
        print('Done')
    except BaseException as err:
        print(f'Fatal error: {err}')
    
    if sess:
        sess.close()
    if school:
        school.close()
    
    input()


if __name__ == '__main__':
    asyncio.run(main())
    