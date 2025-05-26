#include <stdio.h>

// Training example 1
int compute_1(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 1;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_1(100));
    return 0;
}
