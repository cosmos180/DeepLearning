--[[
Author       : bughero bughero2012@gmail.com
Date         : 2025-06-04 19:23:37
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-06-04 19:23:46
FilePath     : /DeepLearning/lua/hello.lua
Description  : 

Copyright (c) 2025 by @Me, All Rights Reserved. 
--]]
print("Hello World")

function fact (n)
    if n == 0 then
      return 1
    else
      return n * fact(n-1)
    end
end

print("enter a number:")
a = io.read("*number")        -- read a number
print(fact(a))