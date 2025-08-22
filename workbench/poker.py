def isstraight(nums):
  if sorted(nums) in [[num for num in range(start, start + 5)] for start in range(2,11)] + [[2,3,4,5,14]]:
    return True

def oakhigh(nums, num):
  for v in range(14,1,-1):
    if len([n for n in nums if n == v]) == num:
      return v

def sechigh(nums):
  for v in range(14,1,-1):
    if len([n for n in nums if n == v]) == 2:
      break
  for v in range(v-1,1,-1):
    if len([n for n in nums if n == v]) == 2:
      return v

def isofakind(nums, num):
  for v in range(2,15):
    if len([n for n in nums if n == v]) >= num:
      return True

def isfullhouse(nums):
  for v in range(2,15):
    for u in range(2,15):
      if len([n for n in nums if n == v]) == 3 and\
          len([n for n in nums if n == u]) == 2:
        return True

def istwopair(nums):
  for v in range(2,15):
    for u in range(2,15):
      if len([n for n in nums if n == v]) == 2 and\
          len([n for n in nums if n == u]) == 2 and u != v:
        return True

def rank(cards):
  nums = [card.number if card.number != 1 else 14 for card in cards]
  suites = [card.suite for card in cards]
  if isstraight(nums) and len(set(suites)) == 1:
    if 14 in nums and 13 in nums:
      return 9000000
    return 8000000 + max(num if num != 14 else 1 for num in nums)
  elif isofakind(nums, 4):
    return 7000000 + oakhigh(nums, 4) * 1000 + oakhigh(nums, 1)
  elif isfullhouse(nums):
    return 6000000 + oakhigh(nums, 3) * 1000 + oakhigh(nums, 2)
  elif len(set(suites)) == 1:
    return 5000000 + max(nums)
  elif isstraight(nums):
    if 14 in nums and 13 in nums:
      return 4000014
    return 4000000 + max(num if num != 14 else 1 for num in nums)
  elif isofakind(nums, 3):
    return 3000000 + oakhigh(nums, 3) * 1000 + oakhigh(nums, 1)
  elif istwopair(nums):
    return 2000000 + oakhigh(nums, 2) * 10000 + sechigh(nums) * 100 + oakhigh(nums, 1)
  elif isofakind(nums, 2):
    return 1000000 + oakhigh(nums, 2) * 1000 + oakhigh(nums, 1)
  else:
    highest = max(nums)
    del nums[nums.index(max(nums))]
    return highest * 1000 + max(nums)

