#include <stdio.h>

// Training example 8
int compute_8(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 8;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_8(100));
    return 0;
}
