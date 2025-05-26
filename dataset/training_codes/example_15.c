#include <stdio.h>

// Training example 15
int compute_15(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 15;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_15(100));
    return 0;
}
