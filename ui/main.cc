#include "VecPosition.h"

using namespace std;

int main(int argc, char const *argv[]){
    queue<VecPosition> targets;

    double range, speed1, speed2, total = 0, x, y;
    int time, number;

    //  输入后续途径点
    cin >> number;
    while (number--){
        cin >> x >> y;
        targets.push(VecPosition(x, y));
    }

    //  设置输出间隔、监测点范围、速度
    cin >> time >> range >> speed1 >> speed2;
    targets.push(VecPosition());

    if (targets.size() > 2){
        total = Run(targets, time, range, speed1, speed2);
    }else{
        return 1;
    }

    return 0;
}