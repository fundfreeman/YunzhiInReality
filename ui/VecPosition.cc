#include "VecPosition.h"

#define MS2S(time) (double(time) / 1000)

using namespace std;

double static EARTH_RADIUS = 6378.137;
double static PI = 3.1415926;
double static MIN = 0.000009;
constexpr int TIME_TO_SLEEP = 1000;


VecPosition operator+(const VecPosition &a, const VecPosition &b){
    return VecPosition(a.getLng() + b.getLng(), a.getLat() + b.getLat());
}
VecPosition operator-(const VecPosition &a, const VecPosition &b){
    return VecPosition(a.getLng() - b.getLng(), a.getLat() - b.getLat());
}
VecPosition operator*(const VecPosition &a, const double b){
    return VecPosition(a.getLng() * b, a.getLat() * b);
}

double VecPosition::getDistanceTo(const VecPosition &that) const {
    double radLat1 = rad(this->getLat());
    double radLat2 = rad(that.getLat());
    double a = radLat1 - radLat2;
    double b = rad(this->getLng()) - rad(that.getLng());
    double s = 2 * asin(sqrt(pow(sin(a / 2), 2) + cos(radLat1) * cos(radLat2) * pow(sin(b / 2), 2)));
    return s * EARTH_RADIUS * 1000;
}

double VecPosition::rad(double d){
    return d * PI / 180.0;
}

VecPosition VecPosition::unit_vector(const VecPosition &pos1, const VecPosition &pos2){
    double distance = pos1.getDistanceTo(pos2);
    return (pos2 - pos1) * (1 / distance);
}

bool achieve(VecPosition pos1, VecPosition pos2, double range){
    return pos1.getDistanceTo(pos2) < range;
}

VecPosition NextPosition(const VecPosition &pos1, const VecPosition &pos2, double time, const double &speed){
    double range = time * speed;
    VecPosition unit = VecPosition::unit_vector(pos1, pos2);
    VecPosition next = pos1 + unit * range;
    double x = range * (rand() % 20 - 10) / 20, y = range * (rand() % 20 - 10) / 20;
    next = next + VecPosition(MIN * x, MIN * y);
    unit = VecPosition::unit_vector(pos1, next);
    double tmp = speed * (1 + double(rand() % 200 - 100) / 1000) * time;
    return pos1 + unit * tmp;
}

double AdjustSpeed(const double &speed,const  double &speed2,const double &total){
    return (total > 800. && speed < speed2) ? speed + .02 : speed;
}

//  targets：[0]:出发位置，[1+]:途径点
double Run(queue<VecPosition> &targets, int time, double range, const double &speed1, const double &speed2){
    VecPosition now = VecPosition(), next = VecPosition(), result = VecPosition();
    unsigned int times = 0;
    double speed = speed1, total = 0;
    if (targets.size() > 2){
        now = targets.front();
        targets.pop();
        next = targets.front();
        targets.pop();
    }

    while (!targets.empty()){
        speed = AdjustSpeed(speed, speed2, total);
        result = NextPosition(now, next, MS2S(time), speed);
        total += now.getDistanceTo(result);
        // cout << "now: " << now.getLng() << "," << now.getLat() << endl;

        cout << times++ << "," << fixed << setprecision(14) << result.getLng() << "," << result.getLat() << "," << now.getDistanceTo(result) / MS2S(time) << "," << total << endl;
        now = result;
        // std::this_thread::sleep_for(std::chrono::milliseconds(int(TIME_TO_SLEEP * time)));

        if (achieve(now, next, range)){
            next = targets.front();
            targets.pop();
        }
    }

    return total;
}