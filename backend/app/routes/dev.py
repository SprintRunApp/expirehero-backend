@router.get("/send-test")
def test_email(db=Depends(get_db)):
    check_and_send(db)
    return {"ok": True}