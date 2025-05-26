#include <stdio.h>

// Training example 19
int compute_19(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 19;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_19(100));
    return 0;
}
