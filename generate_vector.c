#include <stdlib.h>
#include <stdio.h>

void generate_random_vector(const int tamanho, int **vector)
{
    int i;
    *vector = (int *)malloc(tamanho * sizeof(int));

    if(*vector == NULL)
    {
        fprintf(stderr, "Nao foi possivel alocar o vetor\n");
        exit(EXIT_FAILURE);
    }

    for (i = 0; i < tamanho; i++)
    {
        (*vector)[i] = rand() % 300;
    }
}