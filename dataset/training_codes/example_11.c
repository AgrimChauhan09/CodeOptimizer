#include <stdio.h>

// Training example 11
int compute_11(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 11;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_11(100));
    return 0;
}
