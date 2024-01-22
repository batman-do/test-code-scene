from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage

system_prompt_da = SystemMessage(
    content="""You are the world's most trusted Python Data Analyst. You help users write syntactically correct Python code to answer questions about data and to generate beautiful data visualizations."""
)

template = """\
In the following conversation, a human user interacts with an Data Analysis Agent. The human user poses questions, and the AI Agent goes through several steps to provide well-informed answers.

The following is the previous conversation between a human and The Data Analysis Agent:
{history}
Current conversation:
Given an user query, create a syntactically correct Python script that will analysis data and answer request from user.

You must use the following format:

Query: <user question>
Context: <context info>
Analysis: <analysis context in Vietnamese language>
Code: ```python <plotly code>```
Analysis: <analysis code in Vietnamese language>

Some rules you follow:
- Your ouput Code must start and end with ```. Don't include any comments, or explanations at the end.
- You can only import standard libraries from Python, and these external libraries: pandas, numpy, matplotlib, seaborn. 
- You MUST imports necessary libraries to can execute code.
- DO NOT show Query, Context.
- MUST show Analysis, Code.

Example 1:
Query: Chiều cao tối đa của nam giới là bao nhiêu?
Context:
"                 0           1           2
Gender        Male      Female        Male
Height         181         172         178
Weight          89          68          79"
Analysis:
1. Lọc dữ liệu để chỉ bao gồm nam giới
2. Tìm chiều cao tối đa của các hàng kết quả
3. Trả kết quả cho người dùng
Code: ```python
import pandas as pd
import numpy as np

df = pd.read_csv("analysis.csv") # replace with the actual file name and path

filtered_df = df[df["Gender"] == "Male"]
highest_male_height = filtered_df.Height.max()
result = "Height of the highest male: " + highest_male_height
result
```
Analysis:
Biểu đồ cho thấy  chiều cao trung bình của nam giới thường cao hơn nữ giới và cân nặng cũng như vậy. Chiều cao tối đa của nam giới là 181.

Example 2:
Query: Bạn hãy phân tích bài báo sau và vẽ biểu đồ cho phân tích của bạn.
Context:
"[1] Lô đất 19 tỉ nay phải bán 13 tỉ , người trong cuộc chỉ cách cho nhà đầu tư bất động sản không còn bị mất tiền trong năm 2024 . 04-01-2024 - 10:08 AM . Bất động sản . Chia sẻ . Nếu lấy mốc là đầu năm 2022 , đến hiện tại tất cả các phân khúc trên thị trường bất động sản đều ghi nhận giảm giá , ít nhất là 5 % , và ca o nhất là 50 % . 04-01-2024Điểm danh 4 tuyến cao tốc của VEC dự kiến tăng phí từ ngày 1/2 . TIN MỚI . Trong chia sẻ mới đây , ông Lê Quốc Kiên , một nhà đầu tư bất động sản kì cựu tại Tp.HCM đã có những góc nhìn thực tế về giá bất động sản cũng như dành lời khuyên cho nhà đầu tư . Theo ông Kiên , năm 2023 , bất động sả n đã giảm giá ở tất cả các phân khúc . Mức giảm giá khác nhau tùy vào khả năng đáp ứng “ nhu cầu sử dụng cuối ” . Các bất động sản càng để không hoặc chưa thể k hai thác , càng không phục vụ nhu cầu sử dụng cuối càng giảm giá nhiều , ngược lại các bất động sản có thể sử dụng được ngay có mức giảm ít hơn . Lấy mốc so sán h giá là thời điểm đầu năm 2022 , các phân khúc bất động sản đang lần lượt giảm giá cụ thể như : Nhà phố trong dân tại Tp.HCM hiện giảm giá từ 5 % đến 15 % ( đị nh giá giảm chung của các ngân hàng ) . Chung cư hiện đang ghi nhận giảm giá 10-15 % trên thị trường thứ cấp . Chẳng hạn , một dự án chung cư tại quận 9 ( cũ , nay là Tp.Thủ Đức ) hiện một số nhà đầu tư mua 2,8 tỉ đồng/căn , bán ra 2,5 tỉ đồng . Hay mua 2,3 tỉ đồng phải bán 1,8 tỉ đồng . Ông Kiên cụ thể về trường hợp c hị M mua căn hộ giá 2,3 tỉ đồng tại quận 9 . Chị đóng vào 500 triệu đồng , được chủ đầu tư ân hạn gốc hai năm đầu . Ban đầu , chị M tính mua rồi tranh thủ kiếm người bán kiếm chút tiền lời . Thế nhưng , sau thời gian ân hạn nợ gốc vẫn không bán được . Chị M phải làm hồ sơ vay 1,8 tỷ , mỗi tháng đóng khoảng tầm 22 triệu . Sau một năm gồng tiền ngân hàng bị đuối '' , chị M phải chấp nhận bán đúng số tiền vay 1,8 đồng , nghĩa là mất 500 triệu đồng . Lý giải căn hộ thứ cấp giả m giá ở một số dự án , ông Kiên cho hay , có trường hợp do hết thời gian ân hạn lãi gốc từ chủ đầu , nhưng nhà đầu tư vẫn chưa bán ra được nên hết tiền đóng tiế p . Có trường hợp ngân hàng không cho vay tiếp nữa do khi thẩm định lại hồ sơ tín dụng nhà đầu tư bị sụt giảm thu nhập , vì thế không có tiền đóng tiếp vào dự á n . Ngoài ra , do khó khăn tài chính , một số nhà đầu tư cá nhân không có tiền đóng tiếp cho ngân hàng nên rao bán lỗ căn hộ thứ cấp . Đa số những người phải giảm giá bán thứ cấp là dân đầu tư , dự tính chỉ phải bỏ vào 20 % đến 30 % giá trị căn hộ rồi bán lướt ra . Tuy nhiên , trong bối cảnh thị trường khó khăn , ch ưa bán ra được thì hết tiền đóng tiếp '' , ông Kiên cho hay . Như vậy , mức giảm giá căn hộ 10-15 % là trên thị trường thứ cấp , phần lớn rơi vào các nhà đầu tư đuối tài chính nên rao bán ra thời điểm này , không đại diện cho thị trường chung . Riêng giá căn hộ sơ cấp tại Tp.HCM vẫn xu hướng tăng . Nhà phố liền kề tron g dự án , giảm về giá gốc chủ đầu tư thời điểm 2019 - 2020 . Thậm chí , nếu dự án gặp vướng mắc về pháp lý , giá thứ cấp để bán ra được sẽ phải giảm thấp hơn gi á gốc chủ đầu tư cách đây 4 năm . Đất nền vùng ven cách trung tâm dưới 20 km như Củ Chi , Hóc Môn , quận 9 , quận 12 hiện mức giá giảm 15 % đến 30 % . Chẳng hạn , tại huyện Củ Chi lô đất diện tích lớn mua 19 tỷ giao dịch 13 tỷ ; hay lô đất tại quận 9 mua 4,8 tỷ chốt bán 3,6 tỷ Đất nền ở các khu vực tỉnh xa như Long An , Bà Rịa - Vũng Tàu , Bình Phước , Bình Thuận , Lâm Đồng , Đắk Lắk hiện đang giảm giá dao động từ 20 % đến 40 % , thậm chí có nơi mức giảm đã đến 50 % . Tại Lâm Đồng , lô đất mua 850 triệu giờ bán lại 600 triệu chưa được ; tại Bình Phước lô đất cuối 2021 rao bán 1,3 tỷ giờ khách trả không quá 800 triệu Trong khi giá bấ t động sản nghỉ dưỡng về dưới giá gốc chủ đầu tư thời điểm 2019 – 2020 . Nhà đầu tư chuẩn bị tâm thế gì trong năm 2024 . Theo quan điểm của ông Lê Quốc Kiên , n ăm 2024 vẫn là giai đoạn vừa giằng co vừa thăm dò quan sát tình hình cả thị trường bất động sản và những dấu hiệu chuyển biến của nền kinh tế . Nếu không đáp ứn g tốt “ nhu cầu sử dụng cuối ” thì vẫn chưa có nhiều thanh khoản . Chỉ ra phân khúc có thể là kênh kiếm tiền ổn định trong năm 2024 , ông Kiên cho hay , ưu thế sẽ nghiêng về các loại hình bất động sản có khả năng đáp ứng cao cho “ nhu cầu sử dụng cuối ” . Theo đó , nhà ở riêng lẻ và chung cư sẽ dẫn đầu về xu hướng tăng trưởng , dần ổn định lại trước , có thể giá sẽ không giảm nữa nhưng cũng chưa tăng lại , mà đi ngang trong 2-3 quý đầu năm . Trong khi các phân khúc khác sẽ vẫ n giảm giá thêm từ 5-15 % nữa trong năm 2024 thì mới có thanh khoản , thậm chí giảm giá nhưng vẫn khó có giao dịch . Ông Kiên phân tích , người mua bất động sản sẽ có 3 mục tiêu chính : Kỳ vọng tăng giá , tích lũy tài sản giữ tiền chống trượt giá , và nhu cầu sử dụng cuối . Nhu cầu sử dụng cuối của bất động sản không c hỉ là để ở , mà còn để cho thuê , làm “ tư liệu sản xuất kinh doanh ” như xưởng sản xuất , văn phòng công ty , kho bãi , địa điểm bán hàng , nơi trồng trọt chăn nuôi . Khi 2 mục tiêu đầu trong giai đoạn này không phù hợp do các bất động sản đều đang giảm giá , mục tiêu cuối sẽ được ưu tiên . Đất nông nghiệp ở xa có thể khai thác trồng trọt chăn nuôi thì chỉ phù hợp nông dân địa phương hoặc số ít những nhà đầu tư đủ khả năng làm nông nghiệp quy mô lớn , không dành cho đại đa s ố các nhà đầu tư bất động sản , nên chỉ có chung cư và nhà phố trong dân sẽ đáp ứng tốt nhất cho mục tiêu “ sử dụng cuối ” . Tuy nhiên , nhà đầu tư cũng cần lưu ý bản thân chung cư sẽ có 3 nhóm khác nhau : Đáp ứng tốt cho nhu cầu sử dụng cuối , để đầu tư tích lũy , và sử dụng trong tương lai . Nhóm 1 , chung cư để có t hể thuận tiện ở hoặc dễ dàng cho thuê sẽ có mức giá vừa túi tiền , khoảng 30-40 triệu/m2 , đưa vào sử dụng trên 5 năm . Còn chung cư mới có mức giá xấp xỉ 50 tr iệu/m2 ; đồng thời các chung cư này cần nằm gần các khu vực tập trung đông công ty , nhà xưởng sản xuất kinh doanh . Nhóm 2 , các chung cư cao cấp ở vị trí đắc địa có giá cao mang mục đích đầu tư và tích trữ tài sản nhiều hơn . Vì những người đã có điều kiện mua dạng bất động sản này thì thường đã có nhà ở chỗ khác , n ên họ mua với mục đích đầu tư thêm , làm của để dành rồi tranh thủ cho thuê . Tuy nhiên , vì giá trị cao nên giá cho thuê cũng cao theo , số lượng khách có khả năng thuê ít hơn nhóm đầu nên khả năng bị để trống nhiều hơn . Nhóm 3 , chung cư có giá vừa phải nhưng lại nằm ở các khu vực chưa đông công ty hay nhà máy sản x uất kinh doanh . Loại hình này chỉ mang tính đầu tư hoặc để dành cho tương lai , chưa thuận tiện để ở. Nếu cho thuê tạm giá cũng thấp và không dễ . Ông Kiên dẫn chứng , một dự án có hơn 40.000 căn hộ ở khu vực quận 9 , Tp.HCM có tiện ích nội khu khá tốt , vị trí ngay sát khu công nghệ cao . Tuy nhiên , khu công nghệ ca o quận 9 mới khai thác được 30 % công suất cho tổng 2 giai đoạn nên số lượng doanh nghiệp chưa đủ nhiều . Nếu không làm việc ở khu công nghệ cao thì phải di chu yển quá xa để đến nơi ở , không phù hợp để ở ngay . Do đó trong một vài năm tới , nguồn cầu đủ khả năng mua ở và thuê chưa đủ lấp đầy nguồn cung ở đây . PV . Nh ịp sống thị trường ."
Analysis:
Bài báo bạn cung cấp đề cập đến tình hình giảm giá của thị trường bất động sản đối với các phân khúc khác nhau từ đầu năm 2022 đến nay, và dự kiến cho năm 2024. Dưới đây là một bảng tóm tắt mức giảm giá theo từng phân khúc mà bài báo nêu ra:
- Nhà phố trong dân tại Tp.HCM: giảm từ 5% đến 15%
- Chung cư thị trường thứ cấp: giảm từ 10% đến 15%
- Đất nền vùng ven cách trung tâm dưới 20 km (như Củ Chi, Hóc Môn, quận 9, quận 12): giảm 15% đến 30%
- Đất nền ở các tỉnh xa (như Long An, Bà Rịa - Vũng Tàu, Bình Phước, Bình Thuận, Lâm Đồng, Đắk Lắk): giảm từ 20% đến 50%
- Ngoài ra, các dự báo cho năm 2024 đề cập đến khả năng giảm thêm từ 5% đến 15% cho các phân khúc không đáp ứng nhu cầu sử dụng cuối.
Code: {code_3}
Analysis:
Đây là biểu đồ cột, biểu diễn mức giảm giá của các phân khúc bất động sản từ đầu năm 2022 theo dữ liệu từ bài báo:

- "Nhà phố trong dân" tại Tp.HCM, có mức giảm giá thấp nhất là 5% và cao nhất là 15%.
- "Chung cư thị trường thứ cấp", với mức giảm giá từ 10% đến 15%.
- "Đất nền vùng ven", cách trung tâm dưới 20 km, có mức giảm giá từ 15% đến 30%.
- "Đất nền tỉnh xa", mức giảm giá giao động từ 20% đến 50%.
Biểu đồ cho biết sự chênh lệch giữa mức giảm giá thấp nhất và cao nhất cho từng phân khúc. Các cột màu xanh lam biểu diễn mức giảm giá thấp nhất, trong khi phần cộng thêm màu cam biểu diễn mức giảm giá cao nhất so với mức giảm thấp nhất, cung cấp cái nhìn tổng quát về phạm vi giảm giá cho mỗi phân khúc.

Example 3:
Query: Bạn hãy phân tích bài báo sau và vẽ biểu đồ cho phân tích của bạn. 
Context:
Bài báo: 
"[1] Lô đất 19 tỉ nay phải bán 13 tỉ , người trong cuộc chỉ cách cho nhà đầu tư bất động sản không còn bị mất tiền trong năm 2024 . 04-01-2024 - 10:08 AM . Bất động sản . Chia sẻ . Nếu lấy mốc là đầu năm 2022 , đến hiện tại tất cả các phân khúc trên thị trường bất động sản đều ghi nhận giảm giá , ít nhất là 5 % , và ca o nhất là 50 % . 04-01-2024Điểm danh 4 tuyến cao tốc của VEC dự kiến tăng phí từ ngày 1/2 . TIN MỚI . Trong chia sẻ mới đây , ông Lê Quốc Kiên , một nhà đầu tư bất động sản kì cựu tại Tp.HCM đã có những góc nhìn thực tế về giá bất động sản cũng như dành lời khuyên cho nhà đầu tư . Theo ông Kiên , năm 2023 , bất động sả n đã giảm giá ở tất cả các phân khúc . Mức giảm giá khác nhau tùy vào khả năng đáp ứng “ nhu cầu sử dụng cuối ” . Các bất động sản càng để không hoặc chưa thể k hai thác , càng không phục vụ nhu cầu sử dụng cuối càng giảm giá nhiều , ngược lại các bất động sản có thể sử dụng được ngay có mức giảm ít hơn . Lấy mốc so sán h giá là thời điểm đầu năm 2022 , các phân khúc bất động sản đang lần lượt giảm giá cụ thể như : Nhà phố trong dân tại Tp.HCM hiện giảm giá từ 5 % đến 15 % ( đị nh giá giảm chung của các ngân hàng ) . Chung cư hiện đang ghi nhận giảm giá 10-15 % trên thị trường thứ cấp . Chẳng hạn , một dự án chung cư tại quận 9 ( cũ , nay là Tp.Thủ Đức ) hiện một số nhà đầu tư mua 2,8 tỉ đồng/căn , bán ra 2,5 tỉ đồng . Hay mua 2,3 tỉ đồng phải bán 1,8 tỉ đồng . Ông Kiên cụ thể về trường hợp c hị M mua căn hộ giá 2,3 tỉ đồng tại quận 9 . Chị đóng vào 500 triệu đồng , được chủ đầu tư ân hạn gốc hai năm đầu . Ban đầu , chị M tính mua rồi tranh thủ kiếm người bán kiếm chút tiền lời . Thế nhưng , sau thời gian ân hạn nợ gốc vẫn không bán được . Chị M phải làm hồ sơ vay 1,8 tỷ , mỗi tháng đóng khoảng tầm 22 triệu . Sau một năm gồng tiền ngân hàng bị đuối '' , chị M phải chấp nhận bán đúng số tiền vay 1,8 đồng , nghĩa là mất 500 triệu đồng . Lý giải căn hộ thứ cấp giả m giá ở một số dự án , ông Kiên cho hay , có trường hợp do hết thời gian ân hạn lãi gốc từ chủ đầu , nhưng nhà đầu tư vẫn chưa bán ra được nên hết tiền đóng tiế p . Có trường hợp ngân hàng không cho vay tiếp nữa do khi thẩm định lại hồ sơ tín dụng nhà đầu tư bị sụt giảm thu nhập , vì thế không có tiền đóng tiếp vào dự á n . Ngoài ra , do khó khăn tài chính , một số nhà đầu tư cá nhân không có tiền đóng tiếp cho ngân hàng nên rao bán lỗ căn hộ thứ cấp . Đa số những người phải giảm giá bán thứ cấp là dân đầu tư , dự tính chỉ phải bỏ vào 20 % đến 30 % giá trị căn hộ rồi bán lướt ra . Tuy nhiên , trong bối cảnh thị trường khó khăn , ch ưa bán ra được thì hết tiền đóng tiếp '' , ông Kiên cho hay . Như vậy , mức giảm giá căn hộ 10-15 % là trên thị trường thứ cấp , phần lớn rơi vào các nhà đầu tư đuối tài chính nên rao bán ra thời điểm này , không đại diện cho thị trường chung . Riêng giá căn hộ sơ cấp tại Tp.HCM vẫn xu hướng tăng . Nhà phố liền kề tron g dự án , giảm về giá gốc chủ đầu tư thời điểm 2019 - 2020 . Thậm chí , nếu dự án gặp vướng mắc về pháp lý , giá thứ cấp để bán ra được sẽ phải giảm thấp hơn gi á gốc chủ đầu tư cách đây 4 năm . Đất nền vùng ven cách trung tâm dưới 20 km như Củ Chi , Hóc Môn , quận 9 , quận 12 hiện mức giá giảm 15 % đến 30 % . Chẳng hạn , tại huyện Củ Chi lô đất diện tích lớn mua 19 tỷ giao dịch 13 tỷ ; hay lô đất tại quận 9 mua 4,8 tỷ chốt bán 3,6 tỷ Đất nền ở các khu vực tỉnh xa như Long An , Bà Rịa - Vũng Tàu , Bình Phước , Bình Thuận , Lâm Đồng , Đắk Lắk hiện đang giảm giá dao động từ 20 % đến 40 % , thậm chí có nơi mức giảm đã đến 50 % . Tại Lâm Đồng , lô đất mua 850 triệu giờ bán lại 600 triệu chưa được ; tại Bình Phước lô đất cuối 2021 rao bán 1,3 tỷ giờ khách trả không quá 800 triệu Trong khi giá bấ t động sản nghỉ dưỡng về dưới giá gốc chủ đầu tư thời điểm 2019 – 2020 . Nhà đầu tư chuẩn bị tâm thế gì trong năm 2024 . Theo quan điểm của ông Lê Quốc Kiên , n ăm 2024 vẫn là giai đoạn vừa giằng co vừa thăm dò quan sát tình hình cả thị trường bất động sản và những dấu hiệu chuyển biến của nền kinh tế . Nếu không đáp ứn g tốt “ nhu cầu sử dụng cuối ” thì vẫn chưa có nhiều thanh khoản . Chỉ ra phân khúc có thể là kênh kiếm tiền ổn định trong năm 2024 , ông Kiên cho hay , ưu thế sẽ nghiêng về các loại hình bất động sản có khả năng đáp ứng cao cho “ nhu cầu sử dụng cuối ” . Theo đó , nhà ở riêng lẻ và chung cư sẽ dẫn đầu về xu hướng tăng trưởng , dần ổn định lại trước , có thể giá sẽ không giảm nữa nhưng cũng chưa tăng lại , mà đi ngang trong 2-3 quý đầu năm . Trong khi các phân khúc khác sẽ vẫ n giảm giá thêm từ 5-15 % nữa trong năm 2024 thì mới có thanh khoản , thậm chí giảm giá nhưng vẫn khó có giao dịch . Ông Kiên phân tích , người mua bất động sản sẽ có 3 mục tiêu chính : Kỳ vọng tăng giá , tích lũy tài sản giữ tiền chống trượt giá , và nhu cầu sử dụng cuối . Nhu cầu sử dụng cuối của bất động sản không c hỉ là để ở , mà còn để cho thuê , làm “ tư liệu sản xuất kinh doanh ” như xưởng sản xuất , văn phòng công ty , kho bãi , địa điểm bán hàng , nơi trồng trọt chăn nuôi . Khi 2 mục tiêu đầu trong giai đoạn này không phù hợp do các bất động sản đều đang giảm giá , mục tiêu cuối sẽ được ưu tiên . Đất nông nghiệp ở xa có thể khai thác trồng trọt chăn nuôi thì chỉ phù hợp nông dân địa phương hoặc số ít những nhà đầu tư đủ khả năng làm nông nghiệp quy mô lớn , không dành cho đại đa s ố các nhà đầu tư bất động sản , nên chỉ có chung cư và nhà phố trong dân sẽ đáp ứng tốt nhất cho mục tiêu “ sử dụng cuối ” . Tuy nhiên , nhà đầu tư cũng cần lưu ý bản thân chung cư sẽ có 3 nhóm khác nhau : Đáp ứng tốt cho nhu cầu sử dụng cuối , để đầu tư tích lũy , và sử dụng trong tương lai . Nhóm 1 , chung cư để có t hể thuận tiện ở hoặc dễ dàng cho thuê sẽ có mức giá vừa túi tiền , khoảng 30-40 triệu/m2 , đưa vào sử dụng trên 5 năm . Còn chung cư mới có mức giá xấp xỉ 50 tr iệu/m2 ; đồng thời các chung cư này cần nằm gần các khu vực tập trung đông công ty , nhà xưởng sản xuất kinh doanh . Nhóm 2 , các chung cư cao cấp ở vị trí đắc địa có giá cao mang mục đích đầu tư và tích trữ tài sản nhiều hơn . Vì những người đã có điều kiện mua dạng bất động sản này thì thường đã có nhà ở chỗ khác , n ên họ mua với mục đích đầu tư thêm , làm của để dành rồi tranh thủ cho thuê . Tuy nhiên , vì giá trị cao nên giá cho thuê cũng cao theo , số lượng khách có khả năng thuê ít hơn nhóm đầu nên khả năng bị để trống nhiều hơn . Nhóm 3 , chung cư có giá vừa phải nhưng lại nằm ở các khu vực chưa đông công ty hay nhà máy sản x uất kinh doanh . Loại hình này chỉ mang tính đầu tư hoặc để dành cho tương lai , chưa thuận tiện để ở. Nếu cho thuê tạm giá cũng thấp và không dễ . Ông Kiên dẫn chứng , một dự án có hơn 40.000 căn hộ ở khu vực quận 9 , Tp.HCM có tiện ích nội khu khá tốt , vị trí ngay sát khu công nghệ cao . Tuy nhiên , khu công nghệ ca o quận 9 mới khai thác được 30 % công suất cho tổng 2 giai đoạn nên số lượng doanh nghiệp chưa đủ nhiều . Nếu không làm việc ở khu công nghệ cao thì phải di chu yển quá xa để đến nơi ở , không phù hợp để ở ngay . Do đó trong một vài năm tới , nguồn cầu đủ khả năng mua ở và thuê chưa đủ lấp đầy nguồn cung ở đây . PV . Nh ịp sống thị trường ."
Analysis:
Bài báo đề cập đến tình hình giảm giá của thị trường bất động sản tại Việt Nam từ đầu năm 2022 đến nay, với mức giảm giá tối thiểu là 5% và cao nhất là 50%. Để thực hiện phân tích và vẽ biểu đồ, chúng ta cần xác định các thông tin quan trọng:
1. Mức giảm giá tối thiểu và tối đa của thị trường bất động sản.
2. Mức giảm giá cụ thể theo từng phân khúc bất động sản.
3. Những yếu tố ảnh hưởng đến mức giảm giá như khả năng đáp ứng nhu cầu sử dụng cuối, khó khăn tài chính của nhà đầu tư, và vấn đề pháp lý của dự án.
4. Dự đoán cho năm 2024 về xu hướng thị trường và các phân khúc có khả năng phục hồi.
Từ đây, chúng ta có thể tập trung vào việc minh họa mức giảm giá cho từng phân khúc bất động sản và sự biến đổi của giá cả, dựa trên các dữ liệu cụ thể được đề cập:
- Nhà phố trong dân tại Tp.HCM: giảm giá từ 5-15%.
- Chung cư thị trường thứ cấp: giảm giá 10-15%.
- Đất nền vùng ven cách trung tâm dưới 20 km: giảm 15-30%.
- Đất nền ở các khu vực tỉnh xa: giảm từ 20-50%.
- Để phản ánh tình hình này trực quan, chúng ta có thể vẽ biểu đồ cột để so sánh mức giảm giá giữa các phân khúc, và biểu đồ dòng để thể hiện dự đoán giá cho năm 2024.
Tôi sẽ tiến hành vẽ biểu đồ cột để so sánh mức giảm giá giữa các phân khúc bất động sản trước tiên.
Code: {code_1}
Analysis: 
Biểu đồ cột trên mô tả mức giảm giá tối thiểu và tối đa của từng phân khúc bất động sản. Chúng ta có thể thấy:

Nhà phố đã ghi nhận mức giảm giá tối thiểu khoảng 5% và tối đa khoảng 15%.
Chung cư thị trường thứ cấp cũng có mức giảm giá đồng đều từ 10-15%.
Đất nền vùng ven giảm từ 15% đến 30%.
Đất nền ở các khu vực tỉnh xa ghi nhận mức giảm từ 20% đến 50%, phản ánh sự giảm giá đáng kể nhất.
Bây giờ, hãy tiếp tục với việc vẽ biểu đồ dòng để dự đoán xu hướng giá cho năm 2024, dựa trên thông tin rằng một số phân khúc bất động sản có thể sẽ giảm giá thêm từ 5-15% trong năm 2024 hoặc giữ nguyên mức giá hiện tại. Chúng ta sẽ giả định rằng phân khúc nhà phố và chung cư sẽ giữ nguyên giá, trong khi các phân khúc khác giảm thêm 5-15%.
Code: {code_2}
Analysis:
Biểu đồ dòng trên minh họa dự đoán xu hướng giảm giá cho năm 2024 theo từng phân khúc bất động sản. Đường màu xanh biểu diễn mức giảm giá tối thiểu dự kiến và đường màu đỏ biểu diễn mức giảm giá tối đa dự kiến, dựa trên dữ liệu hiện tại và những diễn biến dự đoán cho tương lai.
Chúng ta thấy rằng:
- Nhà phố và chung cư thứ cấp dự kiến sẽ giữ nguyên giá, không ghi nhận mức giảm giá thêm trong năm 2024.
- Đất nền vùng ven và đất nền tỉnh xa có thể chứng kiến sự giảm giá thêm từ 5% đến 15%, điều này sẽ nâng tổng mức giảm lên từ 20% đến 45% cho đất nền vùng ven và từ 25% đến 65% cho đất nền tỉnh xa (do hạn mức tối đa là 100%, mức giảm giá tối đa được điều chỉnh về 100%).
Lưu ý rằng những dự đoán này dựa trên thông tin cung cấp trong bài báo và các giả định được đưa ra đối với tình hình thị trường bất động sản của Việt Nam vào năm 2024. Kết quả cụ thể có thể thay đổi tùy thuộc vào diễn biến của thị trường và kinh tế vĩ mô.

Example 4:
Query: {question}
Context:
{context}
Analysis:

"""
code_1 = """```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Create a DataFrame with the new data
new_data = {
    'Phân khúc': [
        'Nhà phố trong dân tại Tp.HCM', 
        'Chung cư thị trường thứ cấp', 
        'Đất nền vùng ven (dưới 20 km)', 
        'Đất nền tỉnh xa'
    ],
    'Mức giảm giá thấp nhất (%)': [5, 10, 15, 20],
    'Mức giảm giá cao nhất (%)': [15, 15, 30, 50]
}

# New DataFrame
df_new_real_estate = pd.DataFrame(new_data)

# Set the aesthetics for the plots
sns.set(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(10, 6))

# Plot the "Mức giảm giá cao nhất" in lighter shade
sns.barplot(x="Mức giảm giá cao nhất (%)", y="Phân khúc", data=df_new_real_estate,
            label="Mức giảm giá cao nhất (%)", color="salmon", edgecolor='w')

# Plot the "Mức giảm giá thấp nhất" in darker shade
sns.barplot(x="Mức giảm giá thấp nhất (%)", y="Phân khúc", data=df_new_real_estate,
            label="Mức giảm giá thấp nhất (%)", color="darkred", edgecolor='w')

# Add a legend and informative axis label
ax.legend(ncol=2, loc="lower right", frameon=True)
ax.set(xlim=(0, 60), ylabel="", xlabel="Mức giảm giá (%)")
sns.despine(left=True, bottom=True)

# Add title and show the plot
plt.title('Mức giảm giá theo phân khúc bất động sản (từ đầu năm 2022)')
plt.show()
```"""
code_2 = """```python
import matplotlib.pyplot as plt

# Các mảng chứa mức giá giảm cho từng phân khúc
gia_tri_giam_hien_tai = {
    'Nhà phố': [5, 15],
    'Chung cư thứ cấp': [10, 15],
    'Đất nền vùng ven': [15, 30],
    'Đất nền tỉnh xa': [20, 50]
}

# Giả định giá trị giữ nguyên hoặc giảm thêm 5-15% cho từng phân khúc theo dự đoán
du_doan_2024 = {
    'Nhà phố': [0, 0],  # giữ nguyên giá
    'Chung cư thứ cấp': [0, 0],  # giữ nguyên giá
    'Đất nền vùng ven': [5, 15],  # giảm thêm từ 5-15%
    'Đất nền tỉnh xa': [5, 15]  # giảm thêm từ 5-15%
}

# Tính tổng mức giảm giá dự kiến cho năm 2024
gia_tri_giam_toi_thieu_2024 = {}
gia_tri_giam_toi_da_2024 = {}
for pk in phan_khuc:
    gia_tri_giam_toi_thieu_2024[pk] = min(gia_tri_giam_hien_tai[pk][0] + du_doan_2024[pk][0], 100)
    gia_tri_giam_toi_da_2024[pk] = min(gia_tri_giam_hien_tai[pk][1] + du_doan_2024[pk][1], 100)

# Do bất động sản không thể giảm giá quá 100%, chúng ta sẽ hạn chế mức giảm giá ở mức 100%
gia_tri_giam_toi_thieu_2024 = list(gia_tri_giam_toi_thieu_2024.values())
gia_tri_giam_toi_da_2024 = list(gia_tri_giam_toi_da_2024.values())

# Vẽ biểu đồ dòng cho dự đoán năm 2024
fig, ax = plt.subplots(figsize=(10, 6))

# Vẽ đường dự đoán giảm giá tối thiểu và tối đa
plt.plot(phan_khuc, gia_tri_giam_toi_thieu_2024, marker='o', label='Giá giảm tối thiểu dự kiến', color='blue')
plt.plot(phan_khuc, gia_tri_giam_toi_da_2024, marker='o', label='Giá giảm tối đa dự kiến', color='red')

# Đặt tiêu đề và nhãn
plt.title('Dự đoán giảm giá bất động sản cho năm 2024 theo phân khúc')
plt.xlabel('Phân khúc bất động sản')
plt.ylabel('Phần trăm giảm giá (%)')
plt.ylim(0, 100)
plt.xticks(rotation=45)  # Xoay nhãn trục x để dễ đọc

# Hiển thị chú thích
plt.legend()

# Thêm nhãn số liệu cho các điểm
for i, (g_toi_thieu, g_toi_da) in enumerate(zip(gia_tri_giam_toi_thieu_2024, gia_tri_giam_toi_da_2024)):
    ax.annotate(f"{g_toi_thieu}%", (i, g_toi_thieu), textcoords="offset points", xytext=(0,10), ha='center', color='blue')
    ax.annotate(f"{g_toi_da}%", (i, g_toi_da), textcoords="offset points", xytext=(0,10), ha='center', color='red')

plt.tight_layout()  # Tự động điều chỉnh khoảng cách các thành phần trên biểu đồ

# Hiển thị biểu đồ
plt.show()
```"""

code_3 = """```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Create a DataFrame with the provided data
data = {
    'Phân khúc': [
        'Nhà phố trong dân tại Tp.HCM', 
        'Chung cư thị trường thứ cấp', 
        'Đất nền vùng ven (dưới 20 km)', 
        'Đất nền tỉnh xa', 
        'Bất động sản nghỉ dưỡng'
    ],
    'Mức giảm giá thấp nhất (%)': [
        5, 
        10, 
        15, 
        20, 
        None  # Unknown, represented as None for 'Bất động sản nghỉ dưỡng'
    ],
    'Mức giảm giá cao nhất (%)': [
        15, 
        15, 
        30, 
        50, 
        None  # Unknown, represented as None for 'Bất động sản nghỉ dưỡng'
    ]
}

df_real_estate = pd.DataFrame(data)
# Filter out 'Bất động sản nghỉ dưỡng' as it doesn't have specific decrease percentages
df_plot = df_real_estate.dropna()

# Set the aesthetics for the plots
sns.set(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(10, 6))

# Plot the "Mức giảm giá cao nhất" in red
sns.barplot(x="Mức giảm giá cao nhất (%)", y="Phân khúc", data=df_plot,
            label="Mức giảm giá cao nhất (%)", color="r", edgecolor='w')

# Plot the "Mức giảm giá thấp nhất" in blue, add before "Mức giảm giá cao nhất" to avoid overlap
sns.barplot(x="Mức giảm giá thấp nhất (%)", y="Phân khúc", data=df_plot,
            label="Mức giảm giá thấp nhất (%)", color="b", edgecolor='w')

# Add a legend and informative axis label
ax.legend(ncol=2, loc="lower right", frameon=True)
ax.set(xlim=(0, 60), ylabel="", xlabel="Mức giảm giá (%)")
sns.despine(left=True, bottom=True)

# Display the plot
plt.title('Mức giảm giá theo phân khúc bất động sản')
plt.show()
```"""
user_prompt_with_context_da = PromptTemplate(
    template=template,
    input_variables=["context", "question", "history", "code_1", "code_2", "code_3"],
)
