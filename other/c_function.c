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
    float a = 2.0;
    float b = 5.0;
    float x = M_PI;
    float y = cfunc_float(x, a, b);
    printf("y = %.2f*cos(%f*%.2f) = %f\n", b, x, a, y);

    double c = 2.0;
    double d = 5.0;
    double v = M_PI;
    double w = cfunc_double(x, a, b);
    printf("y = %.2f*cos(%f*%.2f) = %f\n", d, v, c, w);

    return 0;
}
