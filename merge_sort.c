#include <time.h>
#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 50

void print_array(int arr[]);
void merge_sort(int arr[], int l, int r);
void merge(int arr[], int l, int m, int r);

int main(void)
{
    int arr[ARRAY_SIZE];
    int i;

    //inicializa seed aleatoria
    srand(time(NULL));

    //Gera numeros aleatorios no array
    for (i = 0; i < ARRAY_SIZE; i++)
        arr[i] = rand() % 100 + 1;

    print_array(arr);

    merge_sort(arr, 0, ARRAY_SIZE - 1);

}

void print_array(int arr[])
{
    int i;

    for (i = 0; i < ARRAY_SIZE; i++)
        printf("%d ", arr[i]);

    printf("\n");
}

void merge_sort(int arr[], int l, int r)
{
    if(l < r)
    {
        int m = l + (r - l) / 2;

        merge_sort(arr, l, m);
        merge_sort(arr, m + 1, r);

        merge(arr, l, m, r);
        print_array(arr);
    }
}

void merge(int arr[], int l, int m, int r)
{
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    int L[n1], R[n2];

    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    i = 0;
    j = 0;
    k = l;
    while (i < n1 && j < n2)
    {
        if (L[i] <= R[j])
        {
            arr[k] = L[i];
            i++;
        }
        else 
        {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1)
    {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2)
    {
        arr[k] = R[j];
        j++;
        k++;
    }
}