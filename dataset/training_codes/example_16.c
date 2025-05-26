#include <stdio.h>

// Training example 16
int compute_16(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 16;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_16(100));
    return 0;
}
