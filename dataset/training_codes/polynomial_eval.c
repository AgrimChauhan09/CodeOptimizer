#include <stdio.h>

double polynomial(double x, double coeffs[], int degree) {
    double result = 0.0;
    double power = 1.0;
    for (int i = 0; i <= degree; i++) {
        result += coeffs[i] * power;
        power *= x;
    }
    return result;
}

int main() {
    double coeffs[] = {1.0, 2.0, 3.0, 4.0};
    double x = 2.5;
    printf("Result: %.2f\n", polynomial(x, coeffs, 3));
    return 0;
}
