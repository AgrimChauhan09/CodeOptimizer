#include <stdio.h>

// Training example 3
int compute_3(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i * 3;
    }
    return result;
}

int main() {
    printf("Result: %d\n", compute_3(100));
    return 0;
}
