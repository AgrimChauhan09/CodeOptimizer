#include <stdio.h>

// Training example 6
int compute_6(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 6;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_6(100));
    return 0;
}
