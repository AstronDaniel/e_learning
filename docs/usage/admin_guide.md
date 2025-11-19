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

## Customizing the Admin Page

### Custom Templates
1. Create a directory named `admin` inside the `templates` directory.
2. Copy the default Django admin templates from the Django installation directory to the `templates/admin` directory.
3. Modify the copied templates to match your desired design.
4. Ensure that the `TEMPLATES` setting in the `e_learning/settings.py` file includes the `templates` directory.

### Custom CSS and JavaScript
1. Create custom CSS and JavaScript files in the `static` directory.
2. Link the custom CSS and JavaScript files in the custom admin templates.
3. Use the existing `static/css/main.css` and `static/js/animations.js` files as a reference.

### Example Customization
1. Create `templates/admin/base_site.html` and `templates/admin/base.html` files.
2. Add the following content to `templates/admin/base_site.html`:
    ```html
    {% extends "admin/base_site.html" %}

    {% block extrastyle %}
        <link rel="stylesheet" type="text/css" href="{% static 'css/admin.css' %}">
    {% endblock %}

    {% block extrahead %}
        <script type="text/javascript" src="{% static 'js/admin.js' %}"></script>
    {% endblock %}
    ```
3. Add the following content to `templates/admin/base.html`:
    ```html
    {% extends "admin/base.html" %}

    {% block extrastyle %}
        <link rel="stylesheet" type="text/css" href="{% static 'css/admin.css' %}">
    {% endblock %}

    {% block extrahead %}
        <script type="text/javascript" src="{% static 'js/admin.js' %}"></script>
    {% endblock %}
    ```
4. Create `static/css/admin.css` and `static/js/admin.js` files.
5. Add custom styles and JavaScript to the created files to enhance the admin page design.
