### Overview
Vedo를 사용, camera 위치 visualize code
camera parameter 
- MVS .txt
- metashape .xml
- matlab .mat
각각 case 마다 intrinsic, extrinsic parsing 하는 방법만 다름
Vedo camera visualize 코드는 고정됨

### .xml to .txt
Metashape 에서 추출한 .xml camera matrix 를 .txt 형식으로 바꿔서 저장함.
origin_offset : Metashape 는 object가 원점에 정렬되어있지 않음(랜덤). origin_offset을 object와 camera location에 빼줌으로써 모든 system을 원점에 정렬함.

