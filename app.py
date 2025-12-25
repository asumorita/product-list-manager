import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(
    page_title="商品リスト管理",
    page_icon="📦",
    layout="wide"
)

# セッション状態の初期化（データ保存用）
if 'products' not in st.session_state:
    st.session_state.products = []

# タイトル
st.title("📦 商品リスト管理ツール")
st.write("仕入れ候補の商品を管理して、利益を一覧で確認できます！")

st.markdown("---")

# 左右2列に分割
col_left, col_right = st.columns([1, 2])

# ===== 左側：商品追加フォーム =====
with col_left:
    st.subheader("➕ 商品を追加")
    
    with st.form("add_product_form", clear_on_submit=True):
        product_name = st.text_input(
            "商品名",
            placeholder="例：ワイヤレスイヤホン",
            help="管理したい商品の名前を入力"
        )
        
        cost_price = st.number_input(
            "🛒 仕入れ価格（円）",
            min_value=0,
            value=1000,
            step=100
        )
        
        selling_price = st.number_input(
            "💴 販売価格（円）",
            min_value=0,
            value=2000,
            step=100
        )
        
        platform = st.selectbox(
            "🏪 販売先",
            ["楽天市場", "Amazon", "Yahoo!ショッピング", "メルカリ"]
        )
        
        submit_button = st.form_submit_button("➕ リストに追加", use_container_width=True)
        
        if submit_button:
            if product_name.strip() == "":
                st.error("❌ 商品名を入力してください")
            else:
                # 手数料率
                fee_rates = {
                    "楽天市場": 10.0,
                    "Amazon": 15.0,
                    "Yahoo!ショッピング": 8.0,
                    "メルカリ": 10.0
                }
                
                fee_rate = fee_rates[platform]
                fee = selling_price * (fee_rate / 100)
                profit = selling_price - cost_price - fee
                
                if cost_price > 0:
                    profit_rate = (profit / cost_price) * 100
                else:
                    profit_rate = 0
                
                # 商品データを作成
                product = {
                    "商品名": product_name,
                    "仕入れ価格": cost_price,
                    "販売価格": selling_price,
                    "販売先": platform,
                    "手数料率": fee_rate,
                    "手数料": int(fee),
                    "利益": int(profit),
                    "利益率": round(profit_rate, 1)
                }
                
                # セッション状態に追加
                st.session_state.products.append(product)
                st.success(f"✅ 「{product_name}」を追加しました！")
                st.rerun()

# ===== 右側：商品リスト表示 =====
with col_right:
    st.subheader("📋 商品リスト")
    
    if len(st.session_state.products) == 0:
        st.info("📭 まだ商品が登録されていません。左側から商品を追加してください。")
    else:
        # 統計情報
        total_products = len(st.session_state.products)
        total_cost = sum([p["仕入れ価格"] for p in st.session_state.products])
        total_selling = sum([p["販売価格"] for p in st.session_state.products])
        total_profit = sum([p["利益"] for p in st.session_state.products])
        
        # メトリクス表示
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("📦 商品数", f"{total_products}個")
        
        with metric_col2:
            st.metric("🛒 仕入れ合計", f"{total_cost:,}円")
        
        with metric_col3:
            st.metric("💴 販売合計", f"{total_selling:,}円")
        
        with metric_col4:
            if total_profit > 0:
                st.metric("💰 利益合計", f"{total_profit:,}円", delta="黒字")
            elif total_profit < 0:
                st.metric("💸 損失合計", f"{abs(total_profit):,}円", delta="赤字", delta_color="inverse")
            else:
                st.metric("⚖️ 損益", "±0円")
        
        st.markdown("---")
        
        # 商品を1つずつ表示
        for idx, product in enumerate(st.session_state.products):
            with st.expander(f"**{idx + 1}. {product['商品名']}** - 利益: {product['利益']:,}円 ({product['利益率']}%)"):
                
                # 2列に分けて表示
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.write(f"**🛒 仕入れ価格:** {product['仕入れ価格']:,}円")
                    st.write(f"**💴 販売価格:** {product['販売価格']:,}円")
                
                with info_col2:
                    st.write(f"**🏪 販売先:** {product['販売先']}")
                    st.write(f"**💸 手数料:** {product['手数料']:,}円 ({product['手数料率']}%)")
                
                st.markdown("---")
                
                # 利益判定
                if product['利益'] > 0:
                    if product['利益率'] >= 30:
                        st.success(f"✅ **利益: {product['利益']:,}円 (利益率: {product['利益率']}%)** 🔥 高利益率！")
                    elif product['利益率'] >= 20:
                        st.success(f"✅ **利益: {product['利益']:,}円 (利益率: {product['利益率']}%)** 👍 良好")
                    else:
                        st.info(f"ℹ️ **利益: {product['利益']:,}円 (利益率: {product['利益率']}%)** 普通")
                elif product['利益'] < 0:
                    st.error(f"❌ **赤字: {abs(product['利益']):,}円 (利益率: {product['利益率']}%)**")
                else:
                    st.warning("⚖️ **利益: ±0円 (トントン)**")
                
                # 削除ボタン
                if st.button(f"🗑️ この商品を削除", key=f"delete_{idx}"):
                    st.session_state.products.pop(idx)
                    st.success(f"✅ 「{product['商品名']}」を削除しました")
                    st.rerun()

st.markdown("---")

# 下部：一括操作
bottom_col1, bottom_col2, bottom_col3 = st.columns(3)

with bottom_col1:
    if st.button("🗑️ 全商品を削除", use_container_width=True):
        st.session_state.products = []
        st.success("✅ 全商品を削除しました")
        st.rerun()

with bottom_col2:
    if len(st.session_state.products) > 0:
        # DataFrameに変換
        df = pd.DataFrame(st.session_state.products)
        
        # CSV形式に変換
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 CSVでダウンロード",
            data=csv,
            file_name="product_list.csv",
            mime="text/csv",
            use_container_width=True
        )

with bottom_col3:
    st.write("")  # スペース調整

# フッター
st.markdown("---")
st.caption("💡 ヒント: データはブラウザを閉じると消えます。CSVでダウンロードして保存しましょう。")
st.caption("Created with ❤️ by Streamlit")
