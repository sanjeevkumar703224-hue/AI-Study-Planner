string Solution::simplifyPath(string A) {
    vector<string> st;
    string cur;

    for (int i = 0; i <= A.size(); i++) {
        if (i == A.size() || A[i] == '/') {
            if (!cur.empty()) {
                if (cur == "..") {
                    if (!st.empty())
                        st.pop_back();
                } else if (cur != ".") {
                    st.push_back(cur);
                }
                cur.clear();
            }
        } else {
            cur += A[i];
        }
    }

    string ans = "/";

    for (int i = 0; i < st.size(); i++) {
        if (i > 0)
            ans += "/";
        ans += st[i];
    }

    return ans;
}
