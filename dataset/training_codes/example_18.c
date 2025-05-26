#include <stdio.h>

// Training example 18
int compute_18(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 18;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_18(100));
    return 0;
}
