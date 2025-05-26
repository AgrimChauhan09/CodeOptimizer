#include <stdio.h>

// Training example 17
int compute_17(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 17;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_17(100));
    return 0;
}
