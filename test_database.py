"""
Test script for Career Path CV Parser.
Tests database connection and ModelExtration operations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.database import (
    test_connection,
    save_model_extration,
    get_model_extration_by_user,
    delete_model_extration
)
from app.schemas.cv_schema import ModelExtrationResponse, Education, Experience


def test_db_connection():
    """Test 1: Database Connection"""
    print("\n" + "=" * 60)
    print("Test 1: Database Connection")
    print("=" * 60)
    
    if test_connection():
        print("✅ SUCCESS - Connected to Career_Path database")
        return True
    else:
        print("❌ FAILED - Cannot connect to database")
        print("   Check your .env file and ODBC Driver installation")
        return False


def test_create_model_extration():
    """Test 2: Create ModelExtration"""
    print("\n" + "=" * 60)
    print("Test 2: Create ModelExtration")
    print("=" * 60)
    
    # Create test data
    test_data = ModelExtrationResponse(
        full_name="Ahmed Test User",
        email="test@example.com",
        phone="+20123456789",
        location="Cairo, Egypt",
        summary="This is a test CV entry",
        skills=["Python", "C#", "SQL Server", "FastAPI"],
        education=[
            Education(
                degree="Bachelor",
                field="Computer Science",
                institution="Test University",
                year="2020"
            )
        ],
        experience=[
            Experience(
                job_title="Software Developer",
                company="Test Company",
                start_date="Jan 2020",
                end_date="Present",
                description="Developing awesome software"
            )
        ],
        certifications=["Test Certification"],
        languages=["Arabic", "English"]
    )
    
    # Use a test user ID (this should exist in AspNetUsers)
    # Replace with actual user ID from your database
    test_user_id = "0191a4b6-c4fc-752e-9d95-40b30fa7a9b6"  # Admin user from migration
    
    try:
        model_id = save_model_extration(test_data, test_user_id)
        print(f"✅ SUCCESS - ModelExtration created with ID: {model_id}")
        return True, test_user_id
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False, None


def test_retrieve_model_extration(user_id: str):
    """Test 3: Retrieve ModelExtration"""
    print("\n" + "=" * 60)
    print("Test 3: Retrieve ModelExtration")
    print("=" * 60)
    
    try:
        data = get_model_extration_by_user(user_id)
        if data:
            print(f"✅ SUCCESS - Retrieved ModelExtration")
            print(f"   Name: {data['full_name']}")
            print(f"   Email: {data['email']}")
            print(f"   Skills: {len(data['skills'])} skills")
            print(f"   Education: {len(data['education'])} entries")
            print(f"   Experience: {len(data['experience'])} entries")
            return True
        else:
            print("⚠️  WARNING - No data found (but no error)")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False


def test_update_model_extration(user_id: str):
    """Test 4: Update ModelExtration"""
    print("\n" + "=" * 60)
    print("Test 4: Update ModelExtration")
    print("=" * 60)
    
    # Create updated data
    updated_data = ModelExtrationResponse(
        full_name="Ahmed Test User (UPDATED)",
        email="updated@example.com",
        phone="+20987654321",
        location="Alexandria, Egypt",
        summary="Updated summary",
        skills=["Python", "C#", "React", "Docker"],
        education=[
            Education(
                degree="Master",
                field="Software Engineering",
                institution="Updated University",
                year="2022"
            )
        ],
        experience=[
            Experience(
                job_title="Senior Developer",
                company="Updated Company",
                start_date="Jan 2022",
                end_date="Present",
                description="Leading development"
            )
        ],
        certifications=["Updated Certification"],
        languages=["Arabic", "English", "French"]
    )
    
    try:
        model_id = save_model_extration(updated_data, user_id)
        print(f"✅ SUCCESS - ModelExtration updated with ID: {model_id}")
        return True
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False


def test_delete_model_extration(user_id: str):
    """Test 5: Delete ModelExtration"""
    print("\n" + "=" * 60)
    print("Test 5: Delete ModelExtration")
    print("=" * 60)
    
    try:
        deleted = delete_model_extration(user_id)
        if deleted:
            print("✅ SUCCESS - ModelExtration deleted")
            return True
        else:
            print("⚠️  WARNING - Nothing to delete")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Career Path CV Parser - Database Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Connection
    if not test_db_connection():
        print("\n❌ Cannot proceed - database not accessible")
        return
    results.append(("Connection", True))
    
    # Test 2: Create
    success, user_id = test_create_model_extration()
    results.append(("Create", success))
    
    if not success or not user_id:
        print("\n⚠️  Skipping remaining tests - create failed")
        print_summary(results)
        return
    
    # Test 3: Retrieve
    results.append(("Retrieve", test_retrieve_model_extration(user_id)))
    
    # Test 4: Update
    results.append(("Update", test_update_model_extration(user_id)))
    
    # Verify update
    test_retrieve_model_extration(user_id)
    
    # Test 5: Delete
    results.append(("Delete", test_delete_model_extration(user_id)))
    
    # Verify deletion
    print("\nVerifying deletion...")
    data = get_model_extration_by_user(user_id)
    if data is None:
        print("✅ Verified - Data successfully deleted")
    else:
        print("⚠️  Warning - Data still exists after delete")
    
    # Summary
    print_summary(results)


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} : {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
