#include <stdio.h>
#include <stdlib.h>

// embedded_systems implementation
int main() {
    // Implementation for embedded_systems
    int data[100];
    for (int i = 0; i < 100; i++) {
        data[i] = i * 2;
    }
    
    int result = 0;
    for (int i = 0; i < 100; i++) {
        result += data[i] * data[i];
    }
    
    printf("Result: %d\n", result);
    return 0;
}
