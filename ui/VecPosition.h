#ifndef _VECPOSITION_

#define _VECPOSITION_

#include <iostream>
#include <queue>
#include <cmath>
#include <thread>
#include <random>
#include <iomanip>

class VecPosition
{
private:
    double Lng;
    double Lat;
public:
    VecPosition(long double x = 0, long double y = 0): Lng(x), Lat(y){};
    double getLng() const {return this->Lng;};
    double getLat() const {return this->Lat;};
    double getDistanceTo(const VecPosition &that) const ;

    static double rad(double d);
    static VecPosition unit_vector(const VecPosition &pos1, const VecPosition &pos2);

    // VecPosition operator+(const VecPosition &a, const VecPosition& b);

    ~VecPosition(){};
};

VecPosition operator+(const VecPosition &a, const VecPosition &b);
VecPosition operator-(const VecPosition &a, const VecPosition &b);
VecPosition operator*(const VecPosition &a, const double b);

bool achieve(VecPosition pos1, VecPosition pos2, double range);
VecPosition NextPosition(const VecPosition &pos1, const VecPosition &pos2, double time, const double &speed);
double AdjustSpeed(const double &speed,const  double &speed2,const double &total);
double Run(std::queue<VecPosition> &targets, int time, double range, const double &speed1, const double &speed2);

#endif