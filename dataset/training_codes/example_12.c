#include <stdio.h>

// Training example 12
int compute_12(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 12;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_12(100));
    return 0;
}
