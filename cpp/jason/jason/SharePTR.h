/*
 * @Author: houjinxin
 * @Date: 2022-09-29 14:45:18
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-09-29 14:51:12
 */
#include <memory>

struct Base {
    Base() { std::cout << "  Base::Base()\n"; }
    // Note: non-virtual destructor is OK here
    ~Base() { std::cout << "  Base::~Base()\n"; }
};

class SharePTR {
  public:
    void test() {
        std::shared_ptr<Base> p = std::make_shared<Base>();

        printf("test: ref count %ld.\n", p.use_count());

        passValue(p);
        passRef(p);
    }

    void passValue(std::shared_ptr<Base> value) {
        printf("passValue: ref count %ld.\n", value.use_count());
    }

    void passRef(std::shared_ptr<Base> &value) {
        printf("passRef: ref count %ld.\n", value.use_count());

        auto tmp = value;
        printf("passRef: ref count %ld.\n", tmp.use_count());
    }
};