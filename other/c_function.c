#include <stdio.h>
#include <math.h>

// Compile with:
// gcc -fPIC -shared -o c_function.so c_function.c

float cfunc1(float x, float a, float b) {
    return b*cos(x*a);
}

int main(int argc, char *argv[]) {
    float a = 2.0;
    float b = 5.0;
    float x = M_PI;
    float y = cfunc1(x, a, b);

    printf("y = %.2f*cos(%f*%.2f) = %f\n", b, x, a, y);

    return 0;
}
