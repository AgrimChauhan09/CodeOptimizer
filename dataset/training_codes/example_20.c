#include <stdio.h>

// Training example 20
int compute_20(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 20;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_20(100));
    return 0;
}
