
# trailing space defines instruciton end

I_CONST = "const "
I_CONST_I4 = "const/4 "
I_CONST_I8 = "const/8 "
I_CONST_I16 = "const/16 "
I_CONST_S = "const-string "
I_MOVE = "move "
I_ADD_I8 = "add-int/lit8 "
I_NEW_INST = "new-instance "
I_CHECK_CAST = "check-cast "
I_MOVE_RESULT_OBJ = "move-result-object "
I_IGET_OBJ = "iget-object "
I_INV_STATIC = "invoke-static "
I_INV_VIRT = "invoke-virtual "

'''
    .line 96
    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;
    .line 97
    move-result-object v2
'''
