#ifndef SERVERIGGLU_H
#define SERVERIGGLU_H

#include <QObject>
#include <QtCore/QList>
#include <QtWebSockets/QWebSocketServer>

class serverIgglu : public QObject
{
    Q_OBJECT
public:
    explicit serverIgglu(quint16 port,QObject *parent = nullptr);
    ~serverIgglu() override;

private slots:
    void onNewConnection();
    void processMessage(const QString &message);
    void socketDisconnected();

private:
    QWebSocketServer *m_pWebSocketServer;
    QList<QWebSocket *> m_clients;
};

#endif // SERVERIGGLU_H
