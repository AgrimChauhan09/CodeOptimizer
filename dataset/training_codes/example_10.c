#include <stdio.h>

// Training example 10
int compute_10(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 10;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_10(100));
    return 0;
}
