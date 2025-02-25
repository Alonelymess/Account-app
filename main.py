import streamlit as st
from datetime import datetime
import pandas as pd
from PIL import Image
from collections import defaultdict
import os
from plotly import express as px

path = 'source/Chi phí mua đồ - 41 Hillcrest - CHUNG.csv'
df = pd.read_csv(path)
df["Ngày"] = pd.to_datetime(df['Ngày'], format='mixed', dayfirst=False)
try:
    df["Giá trị"] = df["Giá trị"].apply(lambda x: float(x.replace(',', '.')))
except:
    pass
try:
    df["Each"] = df["Each"].apply(lambda x: float(x.replace(',', '.')))
except:
    pass
df["Note (người share)"] = df["Note (người share)"].apply(lambda x: x.replace('All', 'Hoàng, Hiếu, Khải, Minh, An, Hải'))
df["Note (người share)"] = df["Note (người share)"].apply(lambda x: x.replace('5', 'Hoàng, Hiếu, Minh, An, Hải'))
df["Note (người share)"] = df["Note (người share)"].apply(lambda x: ['Hoàng, Hiếu, Minh, An, Hải'] if x == 5 else x)

# df['Hóa đơn'] = df['Hóa đơn'].apply(lambda x: f'<a href="{str(x)}" target="_blank"><img src="{str(x)}" width="1000" /></a>' if 'source' in str(x) else x)


# Track changes
if "changes" not in st.session_state:
    st.session_state.changes = []
changes = st.session_state.changes


list_notes = ["All", "5", "Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"]


st.title("Quản lý tiêu dùng")



# Sidebar menu
menu = st.sidebar.selectbox("Select an option", ["Home", "Xem dữ liệu", "Nhập dữ liệu", "Chỉnh sửa", "Xóa dữ liệu", "Thanh toán"])

if menu == "Xem dữ liệu":
    # Date selection
    selected_date = st.date_input("Chọn ngày để xem", datetime.today())

    # Filter DataFrame
    filtered_df = df[df['Ngày'] == pd.to_datetime(selected_date)]

    # Display filtered DataFrame
    if not filtered_df.empty:
        st.write(f"Dữ liệu ngày {selected_date}:")
        st.dataframe(filtered_df, use_container_width=True)
        
        view_receipt = st.checkbox("Xem hóa đơn")
        if view_receipt:
            product = st.selectbox("Chọn mặt hàng", filtered_df['Mặt hàng'].unique())
            path = filtered_df.loc[filtered_df['Mặt hàng'] == product, 'Hóa đơn'].values[0]
            if path:
                # Check if the path exists
                if os.path.exists(path):
                    try:
                        # Open and display the image
                        img = Image.open(path)
                        st.image(img, caption="Hóa đơn", use_container_width=True)
                    except Exception as e:
                        st.error(f"Không thể mở hình ảnh: {e}")
                else:
                    st.warning("Không có hóa đơn, cần bổ sung lại")
        
        pay = st.button("Tính giá tiền (Chỉ ấn lần đầu tiên, sau khi thanh toán không ấn lại!)")
        os.makedirs('source/payments', exist_ok=True)
        if pay:
            payment_dict = defaultdict(list)
            for index, row in filtered_df.iterrows():
                for name in row["Note (người share)"].split(", "):
                    payment_dict[name].append((row["Each"], row['Người chi']))
            
            payment_df = []
            for name, payments_info in payment_dict.items():
                each_payment_detail = {
                    'from': name,
                    'to': {},
                    'date': selected_date
                }

                for each, to in payments_info:
                    if to not in each_payment_detail['to']:
                        each_payment_detail['to'][to] = {
                            'amount': 0,
                            'status': 'Pending'
                        }
                    each_payment_detail['to'][to]['amount'] += each
                    
                    if to == name:
                        each_payment_detail['to'][to]['status'] = 'Done'
                
                payment_df.append(each_payment_detail)
            # st.write(payment_df)
            rows = []
            for payment in payment_df:
                sender = payment['from']
                for receiver, info in payment['to'].items():
                    rows.append({
                        'from': sender,
                        'to': receiver,
                        'date': payment['date'],
                        'amount': info['amount'],
                        'status': info['status']
                    })
                    
            payment_df = pd.DataFrame(rows)
            payment_df = payment_df.sort_values(by=['from', 'to'])
            payment_df.to_csv(f"source/payments/payment_{selected_date}.csv", index=False)
            
            st.success("Đã tính xong")
            
        show_payment = st.button("Xem danh sách thanh toán")
        
        if show_payment:
            st.write(f"Dưới đây là danh sách thanh toán cho ngày {selected_date}:")
            payment_df = pd.read_csv(f"source/payments/payment_{selected_date}.csv")
            st.dataframe(payment_df)
    else:
        st.write("Không có dữ liệu cho ngày đã chọn")
        
elif menu == "Nhập dữ liệu":
    st.subheader("Nhập Dữ Liệu")
    
    os.makedirs('source/images', exist_ok=True)
   
    # Create a form for data entry
    ngày = st.date_input("Ngày", datetime.today())
    mặt_hàng = st.text_input("Mặt hàng (required)")
    loại = st.selectbox("Loại (required)", ["Đồ gia dụng", "Thực phẩm", "Mix"])
    số_lượng = st.number_input("Số lượng (required)", min_value=1)
    giá_trị = st.number_input("Giá trị (tổng) (required)", min_value=0.0)
    người_chi = st.selectbox("Người chi (required)", ["Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"])
    
    # # Create a new list for the multiselect by filtering out the selected spender
    # filtered_notes = [note for note in list_notes if note != người_chi]
    
    notes = st.multiselect("Người share (required)", ["All", "5", "Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"])
    
    if "All" in notes and "5" in notes and len(notes) > 1:
        st.error("Không được chọn người khác nếu chọn 5 hoặc All, vui lòng chọn 5 hoặc All")
    elif "All" in notes and len(notes) > 1:
        st.error("Nếu chọn 'All', không được chọn thêm người khác.")
    elif "5" in notes and len(notes) > 1:
        st.error("Nếu chọn '5', không được chọn thêm người khác.")
    
    if "All" in notes:
        notes = ["Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"]
    elif "5" in notes:
        notes = ["Hoàng", "Hiếu", "Hải", "Minh", "An"]
    
    each = giá_trị / len(notes) if notes else 0
    st.write(f"Mỗi người: {each}")
    
    enable = st.checkbox("Hóa đơn (Ảnh)")
    picture = st.camera_input("Chụp", disabled=not enable)

    if picture:
        img = Image.open(picture)
        img_path = f"source/images/{datetime.today().strftime('%d%m%Y-%H%M%S')}.jpg"
        img.save(img_path)
        st.image(img, caption='Captured Image')

    # Submit button
    submit_button = st.button("Submit")
    
    if submit_button:
        
        # print(notes, each, ngày, mặt_hàng, loại, số_lượng, giá_trị, người_chi)
        
        if not mặt_hàng or not loại or số_lượng <= 0 or giá_trị <= 0 or not notes or not each:
            st.error("Please fill in all required fields.")
            
        else:
            changes.append({
                'Type': 'Append',
                'Ngày': ngày,
                'Mặt hàng': mặt_hàng,
                'Loại': loại,
                'Số lượng': số_lượng,
                'Giá trị': giá_trị,
                'Người chi': người_chi,
                'Note (người share)': ", ".join(notes),
                'Each': each,
                'Hóa đơn': f"source/images/{datetime.today().strftime('%d%m%Y-%H%M%S')}.jpg",
                'Index': len(df)
            })
            # Create a new row with the input data
            new_row = pd.DataFrame({
                'Ngày': [ngày],
                'Mặt hàng': [mặt_hàng],
                'Loại': [loại],
                'Số lượng': [số_lượng],
                'Giá trị': [giá_trị],
                'Người chi': [người_chi],
                'Note (người share)': [", ".join(notes)],  # Join selected notes into a single string
                'Each': [each],
                'Hóa đơn': [f"source/images/{datetime.today().strftime('%d%m%Y-%H%M%S')}.jpg"]  # Store file name
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(path, index=False)
            st.success("Dữ liệu đã được nhập thành công!")
            # os.remove()
            
elif menu == "Chỉnh sửa":
    st.subheader("Chỉnh sửa")
    # Display the existing data
    if not df.empty:
        st.write("Dữ liệu hiện tại:")
        # Date selection for filtering
        selected_date = st.date_input("Chọn ngày để sửa", datetime.today())
        
        # Filter DataFrame by selected date
        filtered_df = df[df['Ngày'] == pd.to_datetime(selected_date)]
        
        if not filtered_df.empty:
            # Select box for choosing an item to edit based on filtered results
            edit_index = st.selectbox(
                "Chọn hàng để chỉnh sửa",
                options=filtered_df.index.tolist(),
                format_func=lambda x: f"{filtered_df.loc[x, 'Mặt hàng']}"
            )
        
            # Edit selected row
            row_to_edit = df.loc[edit_index]
            st.write('---')
            ngày = st.date_input("Đổi ngày", row_to_edit['Ngày'])
            mặt_hàng = st.text_input("Mặt hàng", value=row_to_edit['Mặt hàng'])
            loại = st.selectbox("Loại", ["Đồ gia dụng", "Thực phẩm", "Mix"], index=["Đồ gia dụng", "Thực phẩm", "Mix"].index(row_to_edit['Loại']))
            số_lượng = st.number_input("Số lượng", min_value=1, value=row_to_edit['Số lượng'])
            giá_trị = st.number_input("Giá trị (tổng)", min_value=0.0, value=row_to_edit['Giá trị'])
            người_chi = st.selectbox("Người chi", ["Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"], index=["Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"].index(row_to_edit['Người chi']))
            
            # # Create a new list for the multiselect by filtering out the selected spender
            # filtered_notes = [note for note in list_notes if note != người_chi]
            notes = st.multiselect("Người share", ["All", "5", "Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"], default=row_to_edit['Note (người share)'].split(", "))
            
            if "All" in notes and "5" in notes and len(notes) > 1:
                st.error("Không được chọn người khác nếu chọn 5 hoặc All, vui lòng chọn 5 hoặc All")
            elif "All" in notes and len(notes) > 1:
                st.error("Nếu chọn 'All', không được chọn thêm người khác.")
            elif "5" in notes and len(notes) > 1:
                st.error("Nếu chọn '5', không được chọn thêm người khác.")
            
            if "All" in notes:
                notes = ["Hoàng", "Hiếu", "Khải", "Minh", "An", "Hải"]
            elif "5" in notes:
                notes = ["Hoàng", "Hiếu", "Hải", "Minh", "An"]
                
            each = giá_trị / len(notes) if notes else 0
            st.write(f"Mỗi người: {each}")
            
            submit_button = st.button("Cập nhật dữ liệu")
                
            if submit_button:
                changes.append({
                    'Type': 'Edit',
                    'Ngày': ngày,
                    'Mặt hàng': mặt_hàng,
                    'Loại': loại,
                    'Số lượng': số_lượng,
                    'Giá trị': giá_trị,
                    'Người chi': người_chi,
                    'Note (người share)': ", ".join(notes),
                    'Each': each,
                    'Hóa đơn': row_to_edit['Hóa đơn'],
                    'Index': edit_index
                })
                df.loc[edit_index] = [ngày, mặt_hàng, loại, số_lượng, giá_trị, người_chi, ", ".join(notes), each, row_to_edit['Hóa đơn']]
                df.to_csv(path, index=False)
                st.success("Dữ liệu đã được cập nhật thành công!")
                
            
        else:
            st.write("Không có dữ liệu để chỉnh sửa hoặc xóa.")
            
elif menu == "Xóa dữ liệu":
    st.write("Dữ liệu hiện tại:")
    # Date selection for filtering
    selected_date = st.date_input("Chọn ngày để sửa", datetime.today())
    
    # Filter DataFrame by selected date
    filtered_df = df[df['Ngày'] == pd.to_datetime(selected_date)]
    
    if not filtered_df.empty:
        # Select box for choosing an item to edit based on filtered results
        edit_index = st.selectbox(
            "Chọn hàng để chỉnh sửa",
            options=filtered_df.index.tolist(),
            format_func=lambda x: f"{filtered_df.loc[x, 'Mặt hàng']}"
        )
    
        # Edit selected row
        row_to_edit = df.loc[edit_index]
    # Option to delete the row
    if st.button(f"Xóa dữ liệu {row_to_edit['Mặt hàng']} ngày {row_to_edit['Ngày']}"):
        changes.append({
            'Type': 'Delete',
            'Ngày': row_to_edit['Ngày'],
            'Mặt hàng': row_to_edit['Mặt hàng'],
            'Loại': row_to_edit['Loại'],
            'Số lượng': row_to_edit['Số lượng'],
            'Giá trị': row_to_edit['Giá trị'],
            'Người chi': row_to_edit['Người chi'],
            'Note (người share)': row_to_edit['Note (người share)'],
            'Each': row_to_edit['Each'],
            'Hóa đơn': row_to_edit['Hóa đơn'],
            'Index': edit_index
        })
        df = df.drop(edit_index)
        df.to_csv(path, index=False)
        st.success("Dữ liệu đã được xóa thành công!")
        
elif menu == "Thanh toán":
    

    st.write("Cập nhật trạng thái thanh toán")
    
    # Date selection
    selected_date = st.date_input("Chọn ngày để xem", datetime.today())
    payment_df = pd.read_csv(f"source/payments/payment_{selected_date}.csv")

    From = st.selectbox("From", payment_df['from'].unique())
    To = st.selectbox("To", payment_df['to'].unique())
    
    status_list = ['Pending', 'Done']
    
    status = st.selectbox("Status", status_list, index=status_list.index(payment_df.loc[(payment_df['from'] == From) & (payment_df['to'] == To), 'status'].values[0]))

    confirm_payment = st.button("Confirm payment")

    if confirm_payment:
        try:
            # Update the status in the DataFrame
            payment_df.loc[(payment_df['from'] == From) & (payment_df['to'] == To), 'status'] = status
            
            # Save the updated DataFrame back to the session state
            st.session_state.payment_df = payment_df
            
            # Save to CSV
            payment_df.to_csv(f"source/payments/payment_{selected_date}.csv", index=False)
            
            # Display success message
            st.success("Payment status updated successfully!")

        except Exception as e:
            st.error("Failed to update payment status. Please try again.")
            st.error(str(e))  # Optional: Display the error message for debugging

else:
    # Statistics
    st.subheader("Thống kê")
    time_range = st.date_input("Thời gian", (datetime(2023, 1, 1), datetime.now()))
    filtered_df = df[(df['Ngày'].dt.date >= time_range[0]) & (df['Ngày'].dt.date <= time_range[1])]

    day_df = filtered_df.groupby('Ngày')['Giá trị'].sum().reset_index()
    day_df['Giá trị'] = day_df['Giá trị'].round(2)

    fig = px.bar(day_df, x='Ngày', y='Giá trị', title='Tổng tiền theo ngày')
    st.plotly_chart(fig)
    
# elif menu == "Dữ liệu được chỉnh sửa": 
#     st.dataframe(pd.DataFrame(changes))
#     save = st.button("Save changes?") 
#     if save:
#         try:
#             st.dataframe(df)
#             df.to_csv(data.path, index=False)
#             st.success("Changes saved successfully!")
#         except:
#             st.error("Failed to save changes. Please try again.")


