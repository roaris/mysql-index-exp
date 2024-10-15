# mysql-index-exp
```
mysql> show create table exp;
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                                                                 |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| exp   | CREATE TABLE `exp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `num1` int NOT NULL,
  `num2` int NOT NULL,
  `num3` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1000001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> select count(*) from exp;
+----------+
| count(*) |
+----------+
|  1000000 |
+----------+
1 row in set (0.05 sec)

mysql> select count(distinct num1), count(distinct num2), count(distinct num3) from exp;
+----------------------+----------------------+----------------------+
| count(distinct num1) | count(distinct num2) | count(distinct num3) |
+----------------------+----------------------+----------------------+
|                99995 |                 1000 |                   10 |
+----------------------+----------------------+----------------------+
1 row in set (0.90 sec)
```

## インデックスのイメージ
B-Treeを簡単化して、配列として考えてしまった方が、インデックスについて考えやすいと思っている

num1でインデックスを作成するなら、(id, num1)がnum1の昇順に並んだ配列を考える (ex. `[(2,1), (5,2), (1,2), (4,3), (3,4), (6,5), (7,5)]`)

(num1, num2)でインデックスを作成するなら、(id, num1, num2)が(num1、num2)の昇順に並んだ配列を考える (ex. `[(2,1,2), (5,2,5), (1,2,7), (4,3,1), (3,4,4), (6,5,3), (7,5,6)]`)

(num1, num2 desc)でインデックスを作成するなら、(id, num1, num2)がnum1の昇順に並んで、num1が同じ値の場合はnum2の降順に並んだ配列を考える (ex. `[(2,1,2), (5,2,7), (1,2,5), (4,3,1), (3,4,4), (6,5,6), (7,5,3)]`)

`where num1 >= 3`という条件の場合、num1 >= 3を満たす最左のノードを二分探索で見つけて、そこから右に辿っていく

## カバリングインデックス
`select num3 from exp where num1 = 1;`というクエリを考える

インデックス作成前
```
mysql> select num3 from exp where num1 = 1;
+------+
| num3 |
+------+
|    9 |
|    2 |
|    2 |
|    3 |
|    7 |
|    2 |
|    3 |
|    3 |
+------+
8 rows in set (0.20 sec)

mysql> explain select num3 from exp where num1 = 1;
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
| id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 998360 |    10.00 | Using where |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```
keyがNULLになっている

num1でインデックスを作成する
```
mysql> alter table exp add index num1_index(num1);
Query OK, 0 rows affected (2.90 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num3 from exp where num1 = 1;
+------+
| num3 |
+------+
|    9 |
|    2 |
|    2 |
|    3 |
|    7 |
|    2 |
|    3 |
|    3 |
+------+
8 rows in set (0.00 sec)

mysql> explain select num3 from exp where num1 = 1;
+----+-------------+-------+------------+------+---------------+------------+---------+-------+------+----------+-------+
| id | select_type | table | partitions | type | possible_keys | key        | key_len | ref   | rows | filtered | Extra |
+----+-------------+-------+------------+------+---------------+------------+---------+-------+------+----------+-------+
|  1 | SIMPLE      | exp   | NULL       | ref  | num1_index    | num1_index | 4       | const |    8 |   100.00 | NULL  |
+----+-------------+-------+------------+------+---------------+------------+---------+-------+------+----------+-------+
1 row in set, 1 warning (0.00 sec)
```
速くなった

keyがnum1_indexになっている

num1_indexは削除する
```
mysql> alter table exp drop index num1_index;
Query OK, 0 rows affected (0.02 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

今度は`select num1 from exp where num3 = 1;`というクエリを考える

インデックス作成前
```
mysql> select num1 from exp where num3 = 1;
...
| 58279 |
|  4180 |
| 92453 |
+-------+
99657 rows in set (0.21 sec)

mysql> explain select num1 from exp where num3 = 1;
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
| id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 998360 |    10.00 | Using where |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```

num3でインデックスを作成する
```
mysql> alter table exp add index num3_index(num3);
Query OK, 0 rows affected (3.23 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num1 from exp where num3 = 1;
...
| 58279 |
|  4180 |
| 92453 |
+-------+
99657 rows in set (0.29 sec)

mysql> explain select num1 from exp where num3 = 1;
+----+-------------+-------+------------+------+---------------+------------+---------+-------+--------+----------+-------+
| id | select_type | table | partitions | type | possible_keys | key        | key_len | ref   | rows   | filtered | Extra |
+----+-------------+-------+------------+------+---------------+------------+---------+-------+--------+----------+-------+
|  1 | SIMPLE      | exp   | NULL       | ref  | num3_index    | num3_index | 4       | const | 194126 |   100.00 | NULL  |
+----+-------------+-------+------------+------+---------------+------------+---------+-------+--------+----------+-------+
1 row in set, 1 warning (0.00 sec)
```

今度は遅くなった

インデックスのノードから主キー(idカラム)を特定して、主キーを使ってnum1を取りにいくという挙動になっていて、selectされるレコード数が多いと、ディスクIOが頻発し、かえって遅くなる https://www.softel.co.jp/blogs/tech/archives/5139

こういう時は(num3, num1)でインデックスを作成する

これによってインデックスのノードを見るだけで、num1が分かるようになる
```
mysql> alter table exp drop index num3_index;
Query OK, 0 rows affected (0.03 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> alter table exp add index num3_num1_index(num3, num1);
Query OK, 0 rows affected (3.71 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num1 from exp where num3 = 1;
...
| 99997 |
| 99998 |
| 99999 |
+-------+
99657 rows in set (0.04 sec)

mysql> explain select num1 from exp where num3 = 1;
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------------+
| id | select_type | table | partitions | type | possible_keys   | key             | key_len | ref   | rows   | filtered | Extra       |
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | ref  | num3_num1_index | num3_num1_index | 4       | const | 204368 |   100.00 | Using index |
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```

ExtraのUsing Indexとは、クエリがインデックスだけを用いて解決できることを示す https://zenn.dev/miya_tech/articles/c1b9ca01e90a7b

このような、クエリを処理するのに必要なデータを全て含んでいるようなインデックスを、カバリングインデックスと呼ぶ

不要なカラムをselectすると、カバリングインデックスでなくなってしまうので注意
```
mysql> select * from exp where num3 = 1;
...
|  66536 | 99997 |   54 |    1 |
| 242805 | 99998 |  953 |    1 |
| 417897 | 99999 |  589 |    1 |
+--------+-------+------+------+
99657 rows in set (0.30 sec)

mysql> explain select * from exp where num3 = 1;
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------+
| id | select_type | table | partitions | type | possible_keys   | key             | key_len | ref   | rows   | filtered | Extra |
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------+
|  1 | SIMPLE      | exp   | NULL       | ref  | num3_num1_index | num3_num1_index | 4       | const | 204368 |   100.00 | NULL  |
+----+-------------+-------+------------+------+-----------------+-----------------+---------+-------+--------+----------+-------+
1 row in set, 1 warning (0.00 sec)
```

```
mysql> alter table exp drop index num3_num1_index;
Query OK, 0 rows affected (0.03 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

## ソートに使うインデックス
`select num1 from exp order by num1;`というクエリを考える

```
mysql> select num1 from exp order by num1;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.66 sec)

mysql> explain select num1 from exp order by num1;
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
| id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra          |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
|  1 | SIMPLE      | exp   | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 998360 |   100.00 | Using filesort |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
1 row in set, 1 warning (0.01 sec)
```

ExtraのUsing filesortのfilesortとはクイックソートのこと

https://nippondanji.blogspot.com/2009/03/using-filesort.html

> クエリにORDER BYが含まれる場合、MySQLはある程度の大きさまでは全てメモリ内でクイックソートを処理する。ある程度の大きさとはsort_buffer_sizeであり、これはセッションごとに変更可能である。ソートに必要なメモリがsort_buffer_sizeより大きくなると、テンポラリファイル（テンポラリテーブルではない）が作成され、メモリとファイルを併用してクイックソートが実行される。

num1でインデックスを作成する
```
mysql> alter table exp add index num1_index(num1);
Query OK, 0 rows affected (3.00 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num1 from exp order by num1;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.28 sec)

mysql> explain select num1 from exp order by num1;
+----+-------------+-------+------------+-------+---------------+------------+---------+------+--------+----------+-------------+
| id | select_type | table | partitions | type  | possible_keys | key        | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-------+------------+-------+---------------+------------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | index | NULL          | num1_index | 4       | NULL | 998360 |   100.00 | Using index |
+----+-------------+-------+------------+-------+---------------+------------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```

速くなった

インデックス内のノードを順に辿っていけば良いので、filesortが不要になる

ExtraがUsing filesortからUsing indexになっている

`select num1 from exp order by num1, num2;`だとUsing filesortに戻ってしまう
```
mysql> select num1 from exp order by num1, num2;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.85 sec)

mysql> explain select num1 from exp order by num1, num2;
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
| id | select_type | table | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra          |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
|  1 | SIMPLE      | exp   | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 998360 |   100.00 | Using filesort |
+----+-------------+-------+------------+------+---------------+------+---------+------+--------+----------+----------------+
1 row in set, 1 warning (0.00 sec)
```

num1ではなく(num1, num2)でインデックスを作る
```
mysql> alter table exp drop index num1_index;
Query OK, 0 rows affected (0.04 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> alter table exp add index num1_num2_index(num1, num2);
Query OK, 0 rows affected (3.62 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num1 from exp order by num1, num2;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.30 sec)

mysql> explain select num1 from exp order by num1, num2;
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
| id | select_type | table | partitions | type  | possible_keys | key             | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | index | NULL          | num1_num2_index | 8       | NULL | 998360 |   100.00 | Using index |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```

`select num1 from exp order by num1, num2 desc;`だとUsing index; Using filesortとなる

Using index; Using filesortとなっているのは、以下のように、インデックスとfilesortを組み合わせているためだと考えられる

- Using index : インデックス内のノードを順に辿っていくと、(num1, num2)の昇順になる
- Using filesort : (num1, num2)の昇順に並んでいる状態で、num1の各値について、逆順にすれば良い

```
mysql> explain select num1 from exp order by num1, num2 desc;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.63 sec)

mysql> explain select num1 from exp order by num1, num2 desc;
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-----------------------------+
| id | select_type | table | partitions | type  | possible_keys | key             | key_len | ref  | rows   | filtered | Extra                       |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-----------------------------+
|  1 | SIMPLE      | exp   | NULL       | index | NULL          | num1_num2_index | 8       | NULL | 998360 |   100.00 | Using index; Using filesort |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-----------------------------+
1 row in set, 1 warning (0.00 sec)
```

(num1, num2)ではなく(num1, num2 desc)でインデックスを作成する
```
mysql> alter table exp drop index num1_num2_index;
Query OK, 0 rows affected (0.03 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> alter table exp add index num1_num2_index(num1, num2 desc);
Query OK, 0 rows affected (3.65 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> select num1 from exp order by num1, num2 desc;
...
| 99999 |
| 99999 |
| 99999 |
+-------+
1000000 rows in set (0.30 sec)

mysql> explain select num1 from exp order by num1, num2 desc;
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
| id | select_type | table | partitions | type  | possible_keys | key             | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | exp   | NULL       | index | NULL          | num1_num2_index | 8       | NULL | 998360 |   100.00 | Using index |
+----+-------------+-------+------------+-------+---------------+-----------------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```
