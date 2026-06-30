# 🤖 Vacuum Agent Simulator & CSP Solvers (HCMC Map & 8-Queens)

Chào mừng bạn đến với ứng dụng mô phỏng **Robot hút bụi thông minh** kết hợp các thuật toán giải bài toán ràng buộc **CSP (Constraint Satisfaction Problem)** trực quan hóa bằng đồ họa Pygame.

Ứng dụng này được thiết kế để giúp người mới bắt đầu dễ dàng hình dung cách hoạt động của từng thuật toán Tìm kiếm AI và Lan truyền ràng buộc theo từng bước (Step-by-step).

---

## 📌 Các Tính Năng & Thuật Toán Tích Hợp

### 1. Mô phỏng Robot Hút Bụi (Vacuum Agent)
* **Tìm kiếm mù (Uninformed Search):** BFS (Breadth-First Search), DFS (Depth-First Search), UCS (Uniform Cost Search).
* **Tìm kiếm kinh nghiệm (Informed Search):** Greedy Best-First Search, A* Search.
* **Tìm kiếm nâng cao:** `IDA*` (Iterative Deepening A*), `Beam Search` (Tìm kiếm chùm tia), và `AND-OR Search` trong môi trường có yếu tố ngẫu nhiên/không chắc chắn.

### 2. Tô màu bản đồ TP.HCM (HCMC Map Coloring CSP)
Mục tiêu là tô màu 15 quận/huyện của TP.HCM bằng 4 màu sao cho không có 2 quận nào kề nhau trùng màu:
* **Backtracking thường:** Thử và sai đơn thuần.
* **Backtracking + Forward Checking (FC):** Kiểm tra trước, loại bỏ màu xung đột ở các quận kề ngay lập tức.
* **Backtracking + AC-3 Inference:** Lan truyền ràng buộc nâng cao trên toàn bộ cung đồ thị để cắt tỉa nhánh trống sớm nhất.

### 3. Bài toán 8 Quân hậu (8-Queens)
* **Backtracking (Simple):** Đặt hậu từng cột theo thứ tự mặc định.
* **MRV Heuristic (Minimum Remaining Values):** Ưu tiên chọn cột còn ít ô trống an toàn nhất để đặt trước.
* **Forward Checking:** Loại bỏ sớm các ô bị tấn công ở các cột tiếp theo.
* **Min-Conflicts (Local Search):** Khởi tạo ngẫu nhiên toàn bộ bàn cờ, sau đó liên tục dời quân hậu bị xung đột đến vị trí ít bị tấn công nhất. (Chế độ chạy độc lập không quay lui).

---

## 🛠️ Hướng Dẫn Cài Đặt (Cho Người Mới)

Để chạy được chương trình này, máy tính của bạn cần cài đặt **Python** và thư viện đồ họa **Pygame**. Hãy làm theo 3 bước đơn giản sau:

### Bước 1: Cài đặt Python
1. Tải Python phiên bản mới nhất (khuyên dùng bản 3.10 trở lên) tại trang chủ: [python.org](https://www.python.org/downloads/).
2. **Lưu ý quan trọng khi cài đặt:** Nhớ tích chọn vào ô **`Add Python to PATH`** trước khi bấm *Install Now*.

### Bước 2: Cài đặt thư viện Pygame
1. Mở công cụ dòng lệnh trên máy tính của bạn:
   * **Windows:** Nhấn tổ hợp phím `Windows + R`, gõ `cmd` rồi nhấn *Enter*.
   * **macOS/Linux:** Mở ứng dụng `Terminal`.
2. Gõ câu lệnh sau và nhấn *Enter* để cài đặt tự động:
   ```bash
   pip install pygame

https://github.com/user-attachments/assets/eec26248-e837-4dea-8396-a364cda4690e
