/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2025-04-14 07:20:34
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-14 07:20:37
 * @FilePath     : /DeepLearning/rust/src/practise/r_unittest.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
