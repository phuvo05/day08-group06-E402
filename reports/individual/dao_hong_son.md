# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đào Hồng Sơn  
**Vai trò trong nhóm:** Documentation Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Tôi phụ trách documentation xuyên suốt 4 sprint. Sprint 1 tôi phác thảo `architecture.md` mô tả Indexing flow dựa trên code của Phú. Sprint 2 tôi cập nhật thêm Retrieval và Generation flow sau khi Quân hoàn thành `call_llm()`. Sprint 3 tôi làm việc cùng Định để ghi lại A/B experiment vào `tuning-log.md`: ghi rõ hypothesis, config thay đổi, kết quả đo được và kết luận. Sprint 4 tôi hoàn thiện cả hai file, đảm bảo architecture.md phản ánh đúng pipeline cuối cùng sau khi rerank được tích hợp. Vai trò của tôi là "người quan sát toàn cục" — phải hiểu đủ để mô tả chính xác những gì các thành viên khác làm.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Tôi hiểu rõ hơn về **toàn bộ RAG pipeline** như một hệ thống liên kết, không phải các bước rời rạc. Khi viết `architecture.md`, tôi phải giải thích tại sao mỗi bước tồn tại và kết nối với bước tiếp theo như thế nào. Ví dụ: metadata trong indexing không chỉ là thông tin phụ — nó cho phép filter khi retrieve, ảnh hưởng trực tiếp đến chất lượng context đưa vào LLM.

Ngoài ra tôi hiểu **tuning log quan trọng hơn kết quả**: ghi lại "tại sao chọn variant này" và "A/B rule: chỉ đổi một biến" giúp nhóm tránh lặp lại thí nghiệm và có thể reproduce kết quả sau này.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn là viết `architecture.md` trong khi code vẫn đang thay đổi. Sprint 2 tôi vừa viết xong phần Retrieval thì Định thay đổi số lượng chunk retrieve từ 5 xuống 10 để phục vụ rerank. Phải cập nhật lại. Bài học: nên viết architecture doc sau khi sprint kết thúc, không phải trong khi sprint đang chạy.

Điều ngạc nhiên là việc viết documentation giúp tôi phát hiện ra một inconsistency: `architecture.md` của tôi mô tả pipeline trả về top-3 context cho LLM, nhưng code của Quân đang dùng top-5. Tôi báo lại và Quân fix — documentation không chỉ là ghi chép mà còn là công cụ review.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** "SLA xử lý ticket P1 là bao lâu?"

Tôi chọn câu này vì nó xuất hiện trong cả `tuning-log.md` như case study chính. Baseline trả lời sai ("24 giờ") vì retrieve nhầm chunk từ FAQ chung. Variant rerank sửa được lỗi này, trả lời đúng "4 giờ làm việc" với citation rõ ràng.

Điều thú vị khi nhìn từ góc độ documentation: lỗi này không phải do code sai mà do **corpus ambiguity** — hai document đều nói về SLA nhưng ở mức độ khác nhau. Đây là loại lỗi khó phát hiện nếu chỉ nhìn vào code, nhưng rõ ràng khi nhìn vào scorecard. Tôi ghi điều này vào `tuning-log.md` như một lesson learned cho nhóm.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ tạo **decision log** riêng — ghi lại các quyết định thiết kế quan trọng (tại sao chọn ChromaDB thay vì Pinecone, tại sao dùng paragraph chunking thay vì fixed-size) cùng với lý do và trade-off. Kết quả eval cho thấy nhiều quyết định ban đầu ảnh hưởng lớn đến kết quả cuối, nhưng hiện tại không có chỗ nào ghi lại context của những quyết định đó.
