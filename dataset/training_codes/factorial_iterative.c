#include <stdio.h>

long long factorial(int n) {
    long long result = 1;
    for (int i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}

int main() {
    int n = 20;
    printf("Factorial of %d is %lld\n", n, factorial(n));
    return 0;
}