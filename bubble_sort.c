#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "generate_vector.h"

int main(void)
{
    int tamanho = 0;
    int *vector;

    srand(time(NULL));

    printf("Digite o tamanho do vetor que deseja ordenar: ");
    scanf("%d", &tamanho);

    generate_random_vector(tamanho, &vector);

    free(vector);
}