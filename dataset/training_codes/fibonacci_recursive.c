#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1)
        return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int result = 0;
    for (int i = 0; i < 20; i++) {
        result += fibonacci(i);
    }
    printf("Result: %d\n", result);
    return 0;
}