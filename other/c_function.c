#include <stdio.h>
#include <math.h>

// Compile with:
// gcc -fPIC -shared -o c_function.so c_function.c

float cfunc_float(float x, float a, float b)
{
    return b * cos(x * a);
}

double cfunc_double(double x, double a, double b)
{
    return b * cos(x * a);
}

int main(int argc, char *argv[]) {
    float a1 = 2.0;
    float b1 = 5.0;
    float x1 = M_PI;
    float y1 = cfunc_float(x1, a1, b1);
    printf("y = %.2f*cos(%f*%.2f) = %f\n", b1, x1, a1, y1);

    double a2 = 2.0;
    double b2 = 5.0;
    double x2 = M_PI;
    double y2 = cfunc_double(x2, a2, b2);
    printf("y = %.2f*cos(%f*%.2f) = %f\n", b2, x2, a2, y2);

    return 0;
}
