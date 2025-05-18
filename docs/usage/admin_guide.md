# Admin Guide

This guide provides instructions for administrators of the E-Learning Platform.

## Accessing the Admin Panel

1. Navigate to `/admin` on your site
2. Log in with your superuser credentials

## User Management

### Managing Users
- View all users: Navigate to Users in the admin panel
- Create new users: Click "Add User" and complete the form
- Edit users: Click on a username to modify details
- Delete users: Select users and use the dropdown action menu

### User Roles
- To change a user's role (Student/Instructor):
  - Edit the user profile
  - Change the "is_instructor" field
  - Save changes

## Course Management

### Approving Courses
1. Navigate to Courses in the admin panel
2. Review pending courses (status="pending")
3. Update status to "published" if approved
4. Provide feedback if changes are required

### Featured Courses
1. Select courses to be featured
2. Check the "featured" option
3. Set the display order if necessary

## System Configuration

### Site Settings
- Navigate to the Site Configuration section
- Update general settings:
  - Site name
  - Contact email
  - Registration settings
  - File upload limitations

### Email Configuration
- Configure SMTP settings in the Django settings file
- Test email functionality

## Content Moderation

### Forum Moderation
1. Monitor reported posts
2. Review content flagged by users
3. Take appropriate action (delete, warn, ban)

### Content Review
- Review uploaded materials for policy compliance
- Check for copyright issues in course content

## Reports and Analytics

### Generating Reports
- Access the Reports section
- Select report type and parameters
- Export as CSV or PDF

### System Analytics
- View platform usage statistics
- Monitor server load and performance
- Track user engagement metrics

## Backup and Maintenance

### Database Backup
- Configure automated backups
- Perform manual backups when needed

### System Maintenance
- Schedule maintenance windows
- Notify users of planned downtime
- Update software components
