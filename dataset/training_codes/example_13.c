#include <stdio.h>

// Training example 13
int compute_13(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 13;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_13(100));
    return 0;
}
