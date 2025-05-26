#include <stdio.h>

// Training example 7
int compute_7(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 7;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_7(100));
    return 0;
}
