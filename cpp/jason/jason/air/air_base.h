/*
 * @Author: houjinxin
 * @Date: 2022-10-14 12:06:44
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-14 12:13:40
 */

#ifndef AIR_BASE_H
#define AIR_BASE_H

class AIR_BASE {
  public:
    void test() { doTest(); }

  protected:
    virtual void doTest() {}
};

#endif