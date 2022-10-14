/*
 * @Author: your name
 * @Date: 2020-11-16 18:25:38
 * @LastEditTime: 2021-01-18 19:34:10
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /conan/test_package/target/STLType.h
 */

#include <vector>
#include <type_traits>
#include <typeinfo>
#include <array>

class STLType
{
public:
    void test() {
        std::vector<float> data;
        int myint = 50;
        // std::vector<char> data;
        printf("%ld\n", sizeof(decltype(data)::value_type));
        printf("%s\n", typeid(decltype(data)::value_type).name());
        printf("%s\n", typeid(data).name());

        // int myint = 50;
        // std::string mystr = "string";
        // double *mydoubleptr = nullptr;
        // printf("%s\n", typeid(myint).name()); 
        // std::cout << "myint has type: " << typeid(myint).name() << '\n'
        //         << "mystr has type: " << typeid(mystr).name() << '\n'
        //         << "mydoubleptr has type: " << typeid(mydoubleptr).name() << '\n';

        // std::vector<f>
        // data.resize(10, 100.0f);
        data.reserve(10);
        for (size_t i = 0; i < 5; i++)
        {
            data[i] = 0.88f;            
        }

        for (size_t i = 0; i < 10; i++)
        {
            printf("%f\n", data[i]);
        }

        std::array<int, 0> zeroArray = {};

        printf("zeroArray size == 0\n");
        if constexpr(zeroArray.size() == 0) {
            printf("zeroArray size == 0\n");
        } else {
            printf("zeroArray size != 0\n");
        }

        printf("%s\n", typeid(decltype(zeroArray)::value_type).name());
        
        
    }
};
