## deep-mini 조립하기 
deep-mini를 조립하기 전에 박스 안에 포함 되어 있는 키트구성품을 확인합니다. 구매하신 deep-mini키트 안에는 다음 사진과 같은 키트 구성품이 있습니다. deep-mini는 deepThinkCar-mini의 약칭입니다.

![deep-mini 키트 구성품](https://user-images.githubusercontent.com/96219601/229079095-fdc35c85-dfaf-446f-ba7b-d0f034a821e8.png)

키트의 박스 안에는 키트 패킹 리스트가 있습니다. 키트 패킹 리스트와 실제 구성품이 일치하는지 확인합니다. 
여분의 나사는 패킹 리스트에 기록되어 있지는 않지만 필요합니다. **OS SD카드, 라즈베리파이 보드, 18650 배터리는 포함되어 있지 않습니다. 별도 구매하셔야 합니다. OS SD카드는 [여기](https://github.com/JD-edu/deepThinkCar_mini/blob/main/doc/os.md)를 참고하여 사용자가 스스로 제작할 수 있습니다.** 

### 조립주의사항: 아크릴판은 깨지기 쉬우므로 나사를 체결할 때 너무 힘을 주어서 체결하지 마시기 바랍니다. 

### 1. 아크릴 본체 상판에 앞바퀴 제어용 서보모터 연결  
패킹 리스트를 통해서 구성품을 확인했으면 그 다음에는 아크릴 본체 상판에 앞바퀴 제어용 서보모터를 연결합니다. 다음 번호의 부품을 준비합니다.  

- 1번 아크릴 본체 상판
- 16번 서보모터
- 8번 연결부품
- 조립을 위해 17번 드라이버 렌치
 
![small_IMG_2037](https://user-images.githubusercontent.com/96219601/229279056-007870eb-374a-457a-b15a-f97130f1908e.JPG)

19번 서보키트에서 서보모터만 준비합니다. 서보키트 안에 있는 여러 암(arm)부품과 나사 부품은 나중에 사용 합니다. 부품이 작아서 조립이 조금 어려운 점 참고하십시오. 
8번 연결부품에는 다음 부품이 포함되어 있습니다. 드라이버와 렌치를 이용해서 이 연결 부품을 아크릴 본체 상판에 장착합니다. 

- M2 너트 2개
- M2x8 나사 2개 

아크릴 본체 상판을 확인 하고, 아크릴 상판의 사진을 잘 확인해서 나사로 연결하면 됩니다. 

![small_IMG_2040](https://user-images.githubusercontent.com/96219601/229284840-684d5a5d-93a8-491f-9712-ba097881592c.JPG)

다 조립이 되고 나면 다음과 같은 모습이 됩니다.  
    
![small_IMG_2044](https://user-images.githubusercontent.com/96219601/229284963-d4463e90-0510-4e02-bd25-47acd1c725f9.JPG)

### 2. 라즈베리파이 지지대 연결 
서보모터를 아크릴 상판에 장착한 후에는 라즈베리파이 지지대를 연결해야 합니다. 이 지지대를 미리 연결하지 않으면 배터리 홀더를 연결할 때 불편합니다. 라즈베리파이 지지대를 연결하기 위해서는 다음 부품이 필요합니다.   

- 3 HAT 보드 연결부품 
- 서보모터 부착 아크릴 상판 

![small_IMG_2056](https://user-images.githubusercontent.com/96219601/229290886-404aaeb5-fd5a-4ab2-bbf6-b89fa9b6d6a9.JPG)

3번의 부품 중에서 다음 부품을 사용해서 라즈베리파이 지지대를 조립합니다. 3번의 다른 부품은 나중에 사용하게 됩니다. 

- M2.5x12 PCB 서포터(스페이서) 6개
- M2.5 너트 6개

![small_IMG_2058](https://user-images.githubusercontent.com/96219601/229290753-b200e8a0-18a0-426a-ab33-3fb5fa0a119a.JPG)

라즈베리파이 지지대를 조립하고 나면 다음과 같은 모양이 됩니다. 

![small_IMG_2059](https://user-images.githubusercontent.com/96219601/229290779-e64347d8-2552-41cc-861c-3cbd64c16420.JPG)

### 3. 배터리 홀더의 조립 
라즈베리파이 지지대를 조립한 후에는 배터리홀더를 연결합니다. 배터리홀더를 연결하기 위해서는 다음 구성품이 필요합니다.
**사용가능한 배터리는 18650 충전배터리입니다. 키트에는 포함되어 있지 않습니다. 별도 구매하셔야 합니다. 보호회로가 있고 KC인증을 받은 65mm 사이즈로 구매히셔야 합니다.**

- 아크릴 본체 상판: 서보모터 연결 상태 
- 12번 배터리홀더 
- 5번 배터리홀더 연결 부품 

![small_IMG_2062](https://user-images.githubusercontent.com/96219601/229291096-15427dbb-1a64-4269-a800-ec85cb5196f7.JPG)

- M3x8 접시머리 2개 
- M3 너트 2개 

배터리홀더를 아크릴 본체 상판에서 서보모터가 연결된 반대방향에 부착하고 나사/너트를 연결합니다. 

![small_IMG_2067](https://user-images.githubusercontent.com/96219601/229291138-f984c136-e70b-4513-96a0-33c2622a3f80.JPG)

배터리홀더에 배터리를 넣기 위해서는 돌출부가 없어야 하므로 접시머리를 사용합니다. 조립이 다 된 상황에서는 다음과 같은 모습입니다. 

![small_IMG_2065](https://user-images.githubusercontent.com/96219601/229291175-7b5ecb89-6453-4d0c-8454-fb7e646c9c7b.JPG)

### 4. 카메라 마운트 조립 
배터리 홀더를 조립한 후 카메라 마운트를 아크릴 상판에 조립합니다. 카메라 마운트 조립에 필요한 구성품은 다음고 같습니다. 

- 카메라 마운트 (3D 프린팅)
- 아크릴 상판 어셈블리 
- 6번 카메라 마운트 연결 부품 
  - M3x8 볼트 2개
  - M3 너트 2개 

![small_IMG_2070](https://user-images.githubusercontent.com/96219601/229291464-85eccdf9-009d-49f1-b180-f7e6a8bef95a.JPG)

아래 사진과 같이 M2x8 볼트/너트 2개를 사용해서 카메라 마운트를 아크릴 본체 상판 앞부분에 조립합니다. 완성된 모습은 아래 사진과 같습니다. 

![small_IMG_2071](https://user-images.githubusercontent.com/96219601/229291490-e2d2d1da-d72a-4ec6-903d-98751e7c1827.JPG)


### 5. 뒷바퀴 모터의 조립 
이제 아크릴 본체 하판에 뒷바퀴 모터를 조립할 차례입니다. 뒷바퀴 조립을 위해서 필요한 구성품은 다음과 같습니다.
 
- 13번 뒷바퀴 기어드모터 2개 
- 43mm 뒷바퀴 2개 
- 9 번 뒷바퀴마운트 연결부품 
  - 뒤바퀴 모터브라켓: 2개 
  - M2x8 볼트 4개
  - M2 너트 4개 
- 아크릴 본체 하판 

![small_IMG_2073](https://user-images.githubusercontent.com/96219601/229324454-4a90b464-ff19-4777-ad54-67e459d43a7e.JPG)
![small_IMG_2075](https://user-images.githubusercontent.com/96219601/229324694-b05b24e6-86ec-4ba2-951f-e758fd0b7bf7.JPG)

모터를 조립할 때 모터의 방향에 주의 합니다. 아래 사진처럼 왼쪽 모터는 빨간색 전원선이 위에서 볼 때 위쪽으로 배치합니다. 오른쪽 모터는 빨간색 전원선이 아래쪽으로 가도록 조립합니다.

![small_IMG_2081](https://user-images.githubusercontent.com/96219601/229324677-9595ba36-fd9a-45e3-9b84-f4f5f3b7ae66.JPG)

### 6. 아크릴 상하판 지지대 조립 
뒷바퀴 모터를 조립한 후에는 아크릴 본체 상판과 하판을 지지해줄 지지대를 조립합니다. 지지대 조립을 위해서 필요한 구성품은 다음과 같습니다. 

- 아크릴 본체 파란 어셈블리 
- 4번 상하판 연결 부품 
  - M3x8 볼트 6개 
  - M3x20 PCB 지지대(스페이서) 6개
  - M3 너트 6개
 
![small_IMG_2111](https://user-images.githubusercontent.com/96219601/229324778-7de2bc5a-78c6-45c3-ae24-e256220268ea.JPG)


M3x8 PCB 서포터 6개를 아래 사진과 같이 조립합니다. 6개의 M3 너트는 이후에 아크릴 상하판 조립을 할 때 사용 됩니다. 

![small_IMG_2112](https://user-images.githubusercontent.com/96219601/229324865-932fc1f4-ee60-426b-ad3c-dcaf19985508.JPG)

### 7. 앞바퀴 어셈블리 조립 
아크릴 상하판 조립 전에 앞바퀴 어셈블리를 미리 조립해야 합니다. 앞바퀴 조립에 필요한 구성품은 다음과 같습니다. 

- 2번 좌우 바퀴 홀더 (3D 프린팅)
- 14번 43mm 바퀴 2개 (나머지 2개는 뒷바퀴 조립에 사용됩니다.)
- 10번 앞바퀴 고정용 D-shft 

![small_IMG_2116](https://user-images.githubusercontent.com/96219601/229332161-eb8bbea0-b223-4871-819c-77eb22240100.JPG)

좌우 바퀴 홀더와 43mm 바퀴를 D-shaft를 이용해서 다음과 같이 조립합니다. 좌우 구분이 있습니다. 주의하여 조립해야 합니다. 

![small_IMG_2119](https://user-images.githubusercontent.com/96219601/229332175-ab73adfd-c4aa-4195-9a18-4df7d2cda9e4.JPG)


### 8. 뒷바퀴 조립 
이번에는 남은 2개의 뒷바퀴를 본체에 조립합니다. 조립을 하면 다음과 같이 됩니다. 

![small_IMG_2120](https://user-images.githubusercontent.com/96219601/229332179-e84d9c97-5178-43a5-a443-a4722a3172f7.JPG)

### 9. 앞바퀴 암 어셈블리 조립 

앞바퀴를 본체에 조립하기 전에 앞바퀴 조향에 사용되는 앞바퀴 암 어셉블리를 조립합니다. 앞바퀴 암 어셈블리 조립에 필요한 구성품은 다음과 같습니다.  

- 16번 서보모터 부품 주에서 사용하지 않고 남은 볼트 2개(휠암 나사, 서보암 볼트) 및 서보암 하나 (사진 참고)
- 2번 3D 프린팅 부품 중 휠 암(사진 참고)

![small_IMG_2122](https://user-images.githubusercontent.com/96219601/229334549-4e190392-735a-4b64-adb7-d50575630e56.png)

위 사진의 서보암과 휠암 그리고 휠암 나사를 사용하여 앞바퀴 암 어셈블리를 조립합니다. 서보암 볼트는 나중에 사용되므로 잘 보관합니다. 
완전히 조립이 되면 아래 사진과 같은 모습이 됩니다. 서보암의 여러 나사 구멍 중에서 2번째 나사구멍에 휠 암 나사를 체결하면 됩니다. 너무 깊게 넣으면 서보암이 망가지므로 사진과 같은 정도로만 체결합니다. 

![small_IMG_2124](https://user-images.githubusercontent.com/96219601/229334638-9ed1e7df-3394-4ad7-928e-639caecb98df.JPG)
![small_IMG_2125](https://user-images.githubusercontent.com/96219601/229334645-18b25ee7-1839-4924-900f-9cdef2579ed9.JPG)

### 10. 아크릴 본체 상판 하판 조립 
앞바퀴 암 어셈블리가 조립이 된 후에는 아크릴 본체의 상판과 하판을 조립 합니다. 여기에 사용되는 구성품은 다음과 같습니다. 

- 아크릴 상판 어셈블리 
- 아크릴 하판 어셈블리
- 4번 M3x8 볼트 6개 

![small_IMG_2127](https://user-images.githubusercontent.com/96219601/229334920-d2d0943d-58fc-491b-bdff-db8736140838.JPG)

M3x8 6개의 나사를 다 체결하지말고 우선 뒷바퀴 쪽부터 4개만 체결합니다. 나머지 2개는 앞바퀴의 조립이 완전히 되면 체결합니다. 

![small_IMG_2129](https://user-images.githubusercontent.com/96219601/229334951-31283a5e-1cf5-4d9f-b439-56eb92bbedd0.JPG)

### 11. 앞바퀴 조립 
아크릴 상하판 조립을 한 후에는 앞바퀴를 조립합니다. 앞바퀴 조립에 필요한 구성품은 다음과 같습니다. 

- 자동차 본체 어셈블리 
- 4번 M3x8 볼트 나머지 2개 
- 앞바퀴 어셈블리 좌우 2개 

![small_IMG_2131](https://user-images.githubusercontent.com/96219601/229337504-129116c1-a39a-447a-9322-4420ff2f6c48.JPG)

앞바퀴 어셈블리를 아크릴 자동차 본체에 조립하고 M3x8 볼트 2개를 체결합니다. 이렇게 해서 아크릴 상판 하판 조립이 끝이 났습니다. 
![small_IMG_2132](https://user-images.githubusercontent.com/96219601/229337703-f3de6da6-add9-4ff2-96f3-23a8d5057bfe.JPG)


그 다음에는 앞바퀴 암 어셈블리를 조립합니다. 모두 조립된 모습은 다음과 같습니다. 
![small_IMG_2135](https://user-images.githubusercontent.com/96219601/229337707-70a40aab-9000-4f8e-b223-de70b6dabe91.JPG)

아직 앞바퀴 암 어셈블리와 서보모터를 조립하지 않습니다. 서보모터의 원점을 잡고나서 조립해야 합니다. 

![small_IMG_2137](https://user-images.githubusercontent.com/96219601/229337742-2a47eef9-e80f-4477-a962-9b9bf731da1b.JPG)

### 12. 라즈베리파이 보드 연결 
앞바퀴까지 조립이 끝나면 라즈베리파이 보드와 HAT보드를 조립합니다. deep-mini에 사용할 수 있는 라즈베리파이 보드는 라즈베리파이 3B+, 4 입니다. 라즈베리파이 제로나 라즈베리파이 3A+ 는 사용할 수 없습니다. 또한 3B+ 이전 보드는 성능 문제가 있어서 사용하지 마시기 바랍니다. 라즈베리파이 보드 연결을 위해서는 다음 구성품이 필요합니다. 

- 아크릴 키트 본체 어셈블리  
- **라즈베리파이 보드 (키트에는 포함되어 있지 않습니다. 별도 구매하셔야 합니다.)**
- 3번 HAT보드 연결부품에서 남은 M2.5x8 나사, M2.5x12 PCB서포터 

![small_IMG_2138](https://user-images.githubusercontent.com/96219601/229340160-9d768f12-4fdc-4287-86b2-731b4911c8cb.JPG)

라즈베리파이 보드를 아크릴 키트 본체에 사진의 방향과 같이 올려놓고, M2.5x12 PCB서포터와 M2.5x8 나사로 조립합니다. 
조립된 모습은 다음과 같습니다. 라즈베리파이 GPIO 부분의 2개의 홀에는 M2.5x8  볼트를 체결합니다. 반대편 2개의 홀에는 M2.5x12 PCB 서포터를 체결합니다. 

![small_IMG_2140](https://user-images.githubusercontent.com/96219601/229340129-e90b432e-d142-4603-98f7-87ec524017ff.JPG)

### 13. 카메라 연결 
라즈베리파이 조립이 끝이나면 카메라를 연결합니다. 카메라 연결에 필요한 구성품은 다음과 같습니다. 

- 아크릴 키트 본체 어셈블리
- 15번 카메라 모듈 및 15cm 리본 케이블 
- 7번 카메라 연결 부품 
  - M2x8 볼트 2개 
  - M2 너트 2개 

![small_IMG_2142](https://user-images.githubusercontent.com/96219601/229340264-db1b3140-8076-4d55-ae55-0bc5d56d01a6.JPG)

M2x8 볼트 두개를 이용해서 카메라 마운트 3D 프린팅 기구물에 카매라를 부착합니다. 잘 조립이 되면 다음과 같은 모습이 됩니다. M2 너트 2개로 잘 마무리 합니다. 
![small_IMG_2145](https://user-images.githubusercontent.com/96219601/229341406-71b01ffc-6973-47f1-b219-c16ba92db139.JPG)

카메라를 카메라 마운트에 부착했으면 카메라를 라즈베리파이에 15cm 리본 케이블을 이용하여 연결을 합니다. 리본 케이블을 연결하는 커넥터 위치와 리본 케이블 앞뒤 방향은 다음 사진을 참고합니다. 

![small_IMG_2147](https://user-images.githubusercontent.com/96219601/229341515-c00a57e0-0219-462c-befe-1f5a6e11cf26.JPG)
![small_IMG_2148](https://user-images.githubusercontent.com/96219601/229341524-51cb19a1-125d-471a-a5db-753bff62e8cf.JPG)

### 14. HAT 보드의 조립 
카메라 연결이 끝이나면 그 다음에는 라즈베리파이 위에 탑재되는 HAT 보드를 조립합니다. HAT보드 조립에 필요한 구성품은 다음과 같습니다. 

- 11번 HAT 보드 
- 3번 HAT보드 연결 부품 나머지 M2.5x8 볼트 2개 
- 아크릴 키트 본체 어셈블리 

![small_IMG_2149](https://user-images.githubusercontent.com/96219601/229341675-3eba5029-78cd-4c11-ad70-c28f0636ba6e.JPG)

먼저 HAT보드를 라즈베리파이 GPIO 헤더에 맞추어서 조립합니다. 사진의 빨간색원처럼 라즈베리파이의 GPIO와 HAT의 커넥터가 완전히 일치하도록 조립합니다.  **이때 라즈베리파이 GPIO와 HAT 보드가 정확히 맞아야 합니다. 그렇지 않으면 라즈베리파이의 GPIO 블럭이 고장나서 보드를 사용하지 못하게 될 수도 있습니다.**

![small_IMG_2151](https://user-images.githubusercontent.com/96219601/229346672-578b6041-9427-433a-bd0c-f35126cb19b3.png)

HAT보드를 조립한 다음 3번 연결부품 중 남은 M2.5x8 볼트 두개를 아래 사진과 같이 체결합니다. 이렇게 하면 HAT보드 조립이 끝이 납니다. 

![small_IMG_2152](https://user-images.githubusercontent.com/96219601/229346788-49f68644-7a73-49cb-b4f0-4a6f94df30f2.JPG)

### 15. 배선 
이제까지 원점을 잡기 위해 미루어 두었던 서보모터암 고정을 빼고는 조립이 끝이 났습니다. 이제는 배선을 할 차례입니다. 제일 먼저 사진과 같이 배터리의 전원을 HAT보드 "BAT" 커넥터에 연결 합니다. 다음에는 모터 커넥터를 연결할 차례입니다. 

![small_IMG_2153](https://user-images.githubusercontent.com/96219601/229347065-467dc451-ac93-4c98-ad30-6ba0dc69e6cf.JPG)

모터 커넥터는 아래 사진과 같이 왼쪽 모터의 경우 HAT 보드 오른쪽 모터 커넥터 "M2"에 연결을 합니다. 오른쪽 모터는 반대로 HAT보드 왼쪽 모터 커넥터 "M1"에 연결을 합니다. 

![small_IMG_2155](https://user-images.githubusercontent.com/96219601/229348567-3d59763a-f945-4b7c-a0e9-ea923e07bbcc.png)

서보모터 커넥터는 HAT보드의 "JP1:S1"에 연결을 합니다. 오렌지색상의 신호선이 "S" 표시된 곳에 연결되어야 합니다. 사진을 참고 합니다. 
![small_IMG_2156](https://user-images.githubusercontent.com/96219601/229348662-8b96e33d-1fae-434e-be6b-5c5b88a699e2.JPG)

### 16. SD카드 삽입 
마지막 남은 서보모터 원점을 잡기 위해서는 키트를 부팅해야 합니다. 먼저 구매하거나 스스로 제작한 OS가 담긴 SD카드를 아래 사진과 같이 라즈베리파이에 삽입을 합니다. 그리고 충전된 18650 배터리 2개를 키트 아래쪽 배터리 홀더에 삽입합니다. 

![small_IMG_2161](https://user-images.githubusercontent.com/96219601/229423167-e96690f7-7ef9-4b5b-ae86-d16175c75c88.JPG)

준비가 되면 키트의 라즈베리파이에 키보드/마우스/모니터를 연결하고 HAT 보드 아래쪽에 전원 스위치를 on해서 부팅을 시킵니다. 

![small_IMG_2153_전원](https://user-images.githubusercontent.com/96219601/229423759-6cd4b4c2-b0f5-41dd-b951-78c51daa8896.png)

라즈베리파이가 부팅이 되면, 이제 파일탐색기를 열어서 /deepThinkCar 폴더가 있는지 확인 합니다. 만약 /deepThinkCar 폴더가 없으면 [여기](https://github.com/JD-edu/deepThinkCar_mini) 에서 소스코드를 다운 받습니다. 그리고 test_code 폴더로 이동한 다음 assembly_servo_90.py 코드를 실행합니다.
```
$git clone https://github.com/cobit-git/deepThinkCar.git
$cd test_code
$python3 assembly_servo_90.py
```
이 assembly_servo_90.py 코드는 서보모터를 영점에 위치하도록 해 줍니다. 이렇게 한 후 서보모터 키트에 포함되어 있던 서보암 고정 볼트로 서보모터와 앞바퀴 암 어셈블리를 고정하면 됩니다.

![small_IMG_2157](https://user-images.githubusercontent.com/96219601/229424097-dd4089c6-5ce5-4a82-aa79-ebde96779e8c.JPG)

### 링크
[라즈베리파이 OS 이미지 만들기](https://jd-edu.github.io/deepThinkCar_mini/doc/os)      
[라즈베리파이 소프트웨어 설치 및 셋업](https://jd-edu.github.io/deepThinkCar_mini/doc/setup)       
[deepThinkCar-mini 조립](https://jd-edu.github.io/deepThinkCar_mini/doc/assembly)   
[deepThinkCar-mini 라즈베리파이 VNC 환경 구축](https://jd-edu.github.io/deepThinkCar_mini/doc/vnc)     
[deepThinkCar-mini 하드웨어 테스트](https://jd-edu.github.io/deepThinkCar_mini/doc/hardware)     
[1단계 OpenCV 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_1)        
[2단계 차선인식 데이터 라벨링](https://jd-edu.github.io/deepThinkCar_mini/doc/step_2)      
[3단계 딥러닝 트레이닝](https://jd-edu.github.io/deepThinkCar_mini/doc/step_3)     
[4단계 딥러닝 차선인식 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_4)        
[5단계 딥러닝 오브젝트 디텍팅 주행](https://jd-edu.github.io/deepThinkCar_mini/doc/step_5) 
