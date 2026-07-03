class Solution {
public:
    ListNode* mergeNodes(ListNode* head) {
        ListNode* curr = head->next;
        ListNode* write = head;

        int sum = 0;

        while (curr) {
            if (curr->val == 0) {
                write->next = curr;
                write = curr;
                write->val = sum;
                sum = 0;
            } else {
                sum += curr->val;
            }
            curr = curr->next;
        }

        write->next = nullptr;
        return head->next;
    }
};
