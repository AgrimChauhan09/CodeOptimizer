#include <stdio.h>

// Training example 4
int compute_4(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 4;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_4(100));
    return 0;
}
