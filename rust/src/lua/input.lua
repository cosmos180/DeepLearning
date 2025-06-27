--[[
Author       : bughero bughero2012@gmail.com
Date         : 2025-06-05 18:53:16
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-06-06 12:29:25
FilePath     : /DeepLearning/rust/src/lua/input.lua
Description  : 

Copyright (c) 2025 by @Me, All Rights Reserved. 
--]]

-- defines a factorial function
function fact (n)
    if n == 0 then
      return 1
    else
      return n * fact(n-1)
    end
  end
  
-- print("enter a number:")
-- a = io.read("*number")        -- read a number
-- print(fact(a))


print(b)  --> nil
b = 20
print(b)  --> 10

--[[
    print(10)         -- no action (comment)
--]]


---[[
print(10)         --> 10
--]]

function calculate_crop_QRCode_rect(raw_frame_width, raw_frame_height, left, top, right, bottom)
  local ret = { 0.0, 0.0, 0.0, 0.0 }

  -- 限制在可见区域
  local visible_x1 = math.min(math.max(0.0, left), raw_frame_width)
  local visible_x2 = math.min(math.max(0.0, right), raw_frame_width)
  local visible_y1 = math.min(math.max(0.0, top), raw_frame_height)
  local visible_y2 = math.min(math.max(0.0, bottom), raw_frame_height)
  local visible_w = visible_x2 - visible_x1
  local visible_h = visible_y2 - visible_y1

  local visible_center_x = (visible_x2 + visible_x1) / 2.0

  local adjust_w = visible_w
  if visible_h / visible_w > 1.3 then
      adjust_w = adjust_w * 1.6
      if adjust_w > visible_h then
          adjust_w = visible_h
      end
  end

  local adjust_x1 = visible_center_x - adjust_w / 2.0
  local adjust_x2 = visible_center_x + adjust_w / 2.0

  adjust_x1 = math.min(math.max(0.0, adjust_x1), raw_frame_width)
  adjust_x2 = math.min(math.max(0.0, adjust_x2), raw_frame_width)

  local final_x1 = math.floor(adjust_x1)
  local final_x2 = math.floor(adjust_x2)
  local final_y1 = math.floor(visible_y1)
  local final_y2 = math.floor(visible_y2)

  if final_y2 == 1088 and raw_frame_height == 1088 then
      final_y2 = final_y2 - 16
  end

  local function align_downto_16bit(x)
      return x - (x % 16)
  end

  local final_w = align_downto_16bit(final_x2 - final_x1)
  local final_h = align_downto_16bit(final_y2 - final_y1)

  if final_w == 0 or final_h == 0 then
      print(string.format("[calculate_crop_QRCode_rect] error: final_w=%d, final_h=%d", final_w, final_h))
      return ret
  end

  ret = { final_x1 * 1.0, final_y1 * 1.0, final_w * 1.0, final_h * 1.0 }
  return ret
end


-- -- 示例输入参数
-- local raw_frame_width = 1920
-- local raw_frame_height = 1080
-- local left = 100.0
-- local top = 150.0
-- local right = 600.0
-- local bottom = 800.0

-- -- 调用函数
-- local crop_rect = calculate_crop_QRCode_rect(raw_frame_width, raw_frame_height, left, top, right, bottom)

-- -- 输出结果
-- print(string.format("Crop Rect: x=%.1f, y=%.1f, w=%.1f, h=%.1f",
--     crop_rect[1], crop_rect[2], crop_rect[3], crop_rect[4]))