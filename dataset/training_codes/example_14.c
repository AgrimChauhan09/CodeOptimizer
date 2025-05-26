#include <stdio.h>

// Training example 14
int compute_14(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 14;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_14(100));
    return 0;
}
